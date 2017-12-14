# django stuff
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.files import File
from django.core.servers.basehttp import FileWrapper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext

# podmin app stuff
from podmin.models import Podcast, Episode
from podmin.forms import PodcastForm, EpisodeForm
from podmin.views.helpers import *

# python stuff
import time
import logging
import os

logger = logging.getLogger(__name__)

def podcasts(request):
    """
    all podcasts
    """
    podcasts = Podcast.objects.all()
    request_context = RequestContext(request)
    request_context.push({'podcasts': podcasts})

    return render(request, 'podmin/site/podcasts.html', request_context)

def podcast(request, slug):
    """
    Main page for a specific podcast
    """
    user, manager, editor, webmaster = user_role_check(request, slug)

    podcast = get_object_or_404(Podcast, slug=slug)

    if manager or editor or user.is_superuser:
        episode_list = podcast.episode_set.all().order_by('-pub_date')
    else:
        episode_list = Episode.objects.filter(
            podcast__slug=slug,
            active=True).exclude(published__isnull=True).order_by('-pub_date')

    paginator = Paginator(episode_list, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')

    try:
        episodes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        episodes = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        episodes = paginator.page(paginator.num_pages)

    request_context = RequestContext(request)
    request_context.push({'podcast': podcast, 'episodes': episodes,
                          'manager': manager, 'editor': editor,
                          'webmaster': webmaster})

    return render(request, 'podmin/podcast/podcast.html', request_context)


@login_required
def edit_podcast(request, slug):
    """
    Edit a specific podcast
    """
    user, manager, editor, webmaster = user_role_check(request, slug)

    if not manager and not user.is_superuser:
        message = """I'm sorry {0}, I'm afraid I can't let you
                     edit {1}""".format(user, slug)

        messages.warning(request, message)
        return_url = reverse('podcast_show', kwargs={'slug': slug})
        return render(request, 'podmin/site/denied.html',
            {'return_url': return_url})

    podcast = Podcast.objects.get(slug=slug)
    form = PodcastForm(instance=podcast)

    form.fields['slug'].widget.attrs['readonly'] = True

    if request.method == 'POST':
        form = PodcastForm(request.POST, request.FILES, instance=podcast)
        if form.is_valid():
            messages.success(request, '{0} updated.'.format(podcast.title))
            podcast = form.save()
            podcast.publish()
            return HttpResponseRedirect(reverse('podcast_show',
                                                kwargs={'slug': slug}))


    context = {'form': form, 'slug': slug, 'podcast': podcast}

    return render(request, 'podmin/podcast/podcast_edit.html', context)


@login_required
def new_podcast(request):
    """
    Create a new podcast
    """
    if not request.user.is_superuser:
        message = """I'm sorry {0} I'm afraid I can't let you create a
                     podcast.""".format(request.user)

        messages.warning(request, message)
        return_url = reverse('user_home')
        return render(request, 'podmin/site/denied.html',
            {'return_url': return_url})

    form = PodcastForm()
    if request.method == 'POST':
        form = PodcastForm(request.POST, request.FILES)
        if form.is_valid():
            podcast = form.save(commit=False)
            try:
                request.FILES['image'].content_type is True
            except:
                # no image, use the default

                default_image = os.path.join(settings.STATIC_ROOT,
                                             "img/default_podcast.png")
                with open(default_image) as f:
                    image = File(f)
                    podcast.image.save("default_podcast.png", image, save=True)

            podcast.save()
            messages.success(request, 'Successfully created {0}.'.format(
                podcast.title))

            return HttpResponseRedirect(
                reverse('podcast_show', kwargs={'slug': podcast.slug}))

    return render(request, 'podmin/podcast/podcast_edit.html',
                  {'form': form})


@login_required
def delete_podcast(request, slug):
    """
    Delete a podcast. The post-delete handler will delete all the associated
    files.
    """
    user, manager, editor, webmaster = user_role_check(request, slug)
    if not manager and not user.is_superuser:
        message = "I'm sorry {0}, I'm afraid I can't let you delete {1}".format(
            user, slug)

        messages.warning(request, message)
        return_url = reverse('podcast_show', kwargs={'slug': slug})
        return render(request, 'podmin/site/denied.html',
            {'return_url': return_url})


    podcast = get_object_or_404(Podcast, slug=slug)

    if request.method == 'POST':
        if request.POST.get('confirmed', False):
            podcast.delete()
            messages.success(request, 'Successfully deleted {0}.'.format(
                podcast.title))
            return HttpResponseRedirect(reverse('index'))

    return render(request, 'podmin/podcast/podcast_delete.html',
                  {'podcast': podcast})
