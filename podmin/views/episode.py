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


def episode(request, eid, slug):
    """
    View a specific episode
    """
    user, manager, editor, webmaster = user_role_check(request, slug)

    episode = get_object_or_404(Episode, pk=eid)

    request_context = RequestContext(request)
    request_context.push({'episode': episode, 'manager': manager,
                          'editor': editor, 'webmaster': webmaster})

    return render(request, 'podmin/episode/episode.html', request_context)


@login_required
def edit_episode(request, eid, slug):
    """
    Edit an episode
    """
    user, manager, editor, webmaster = user_role_check(request, slug)

    if not user.is_superuser:
        if not manager and not editor:
            message = """I'm sorry {0}, I'm afraid I can't let you edit episode
                         {1}""".format(user, eid)

            messages.warning(request, message)
            return_url = reverse('episode_show',
                                 kwargs={'eid': eid, 'slug': slug})

            return render(request, 'podmin/site/denied.html',
                          {'return_url': return_url})

    episode = Episode.objects.get(pk=eid)

    if request.method == 'POST':
        form = EpisodeForm(request.POST, request.FILES, instance=episode)

        if form.is_valid():
            episode = form.save(commit=False)
            try:
                episode.size = request.FILES['buffer_audio'].size
                episode.image_type = request.FILES['buffer_image'].content_type
            except:
                pass
            try:
                episode.mime_type = request.FILES['buffer_audio'].content_type
            except:
                pass
            episode.save()

            episode.process_images()

            if episode.podcast.tag_audio:
                episode.tag()

            episode.podcast.publish()

            messages.success(request, '{0}, {1} saved and published.'.format(
                episode.podcast.title, episode.title))

            return HttpResponseRedirect(reverse(
                'episode_show',
                kwargs={'eid': episode.id, 'slug': slug}))

    else:
        form = EpisodeForm(instance=episode)

        form.fields['guid'].widget.attrs['readonly'] = True

    return render(request,
                  'podmin/episode/episode_edit.html',
                  {'form': form, 'episode': episode})

@login_required
def new_episode(request, slug):
    """
    Create a new episode
    """

    user, manager, editor, webmaster = user_role_check(request, slug)

    if not user.is_superuser:
        if not manager and not editor:
            message = """I'm sorry {0}, I'm afraid I can't let you create an
                         episode for {1}""".format(user, slug)

            messages.warning(request, message)
            return_url = reverse('podcast_show', kwargs={'slug': slug})

            return render(request, 'podmin/site/denied.html',
                {'return_url': return_url})

    podcast = get_object_or_404(Podcast, slug=slug)

    guid = "%s%s" % (slug, time.time())

    form = EpisodeForm(initial={'guid': guid})

    if request.method == 'POST':
        form = EpisodeForm(request.POST, request.FILES)
        if form.is_valid():
            episode = form.save(commit=False)
            episode.podcast = podcast
            episode.size = request.FILES['buffer_audio'].size
            try:
                episode.image_type = request.FILES['buffer_image'].content_type
            except:
                pass
            try:
                episode.mime_type = request.FILES['buffer_audio'].content_type
            except:
                pass

            episode.save()

            episode.post_process()

            episode.podcast.publish()
            messages.success(request, '{0} created and published.'.format(
                episode.podcast.title))

            return HttpResponseRedirect(reverse(
                'episode_show',
                kwargs={'eid': episode.id, 'slug': slug}))

    return render(request, 'podmin/episode/episode_edit.html',
                  {'form': form, 'podcast': podcast})


@login_required
def delete_episode(request, eid, slug):
    """
    Delete an episode
    """
    user, manager, editor, webmaster = user_role_check(request, slug)
    # TODO: use if True in () here instead
    if not user.is_superuser:
        if not manager and not editor:
            message = """I'm sorry {0}, I'm afraid I can't let you delete
                         episode {1}""".format(user, eid)
            messages.warning(request, message)

            return_url = reverse('episode_show',
                kwargs={'eid': eid, 'slug': slug})

            return render(request, 'podmin/site/denied.html',
                {'return_url': return_url})

    episode = get_object_or_404(Episode, id=eid)

    if request.method == 'POST':
        if request.POST.get('confirmed', False):
            episode.delete()

            messages.success(request, 'Deleted episode {0}.'.format(
                episode.title))

            return HttpResponseRedirect(reverse('podcast_show',
                                                kwargs={'slug': slug}))

    return render(request, 'podmin/episode/episode_delete.html',
                  {'episode': episode})


@login_required
def depublish_episode(request, eid, slug):
    """
    Move an episodes files back into the buffer, and take the episode
    out of the feed
    """
    user, manager, editor, webmaster = user_role_check(request, slug)

    if not user.is_superuser:
        if not manager and not editor:
            message = """I'm sorry {0}, I'm afraid I can't let you depublish
                         episode {1}""".format(user, eid)
            messages.warning(request, message)

            return_url = reverse('episode_show',
                kwargs={'eid': eid, 'slug': slug})

            return render(request, 'podmin/site/denied.html',
                {'return_url': return_url})

    episode = get_object_or_404(Episode, id=eid)

    episode.depublish()
    episode.podcast.publish_feed()

    messages.success(request, 'Depublished episode {0}.'.format(
        episode.title))

    return HttpResponseRedirect(reverse('podcast_show', kwargs={'slug': slug}))


@login_required
def publish_episode(request, eid, slug):
    """
    Move an existing episode's files from the buffer back into production
    and add the episode back to the feed
    """
    user, manager, editor, webmaster = user_role_check(request, slug)

    if not user.is_superuser:
        if not manager and not editor:
            message = """I'm sorry {0}, I'm afraid I can't let you publish
                         episode {1}""".format(user, eid)

            messages.warning(request, message)

            return_url = reverse('episode_show',
                kwargs={'eid': eid, 'slug': slug})

            return render(request, 'podmin/site/denied.html',
                {'return_url': return_url})

    episode = get_object_or_404(Episode, id=eid)

    episode.publish()
    episode.podcast.publish_feed()

    messages.success(request, 'Published episode {0}.'.format(
        episode.title))

    return HttpResponseRedirect(reverse('podcast_show', kwargs={'slug': slug}))


@login_required
def mothball_episode(request, eid, slug):
    """
    Move an existing episode's files from the buffer into the archive and
    save its serialized episode object
    """
    user, manager, editor, webmaster = user_role_check(request, slug)

    if not user.is_superuser:
        if not manager and not editor:
            message = """I'm sorry {0}, I'm afraid I can't let you mothball
                         episode {1}""".format(user, eid)
            messages.warning(request, message)

            return_url = reverse('episode_show',
                kwargs={'eid': eid, 'slug': slug})

            return render(request, 'podmin/site/denied.html',
                {'return_url': return_url})

    episode = get_object_or_404(Episode, id=eid)

    if episode.active or episode.published:
        message = """I'm sorry {0}, before you can mothball an episode, it must
                     be inactive and not published.""".format(user)

        messages.warning(request, message)

        return_url = reverse('episode_show', kwargs={'eid': eid, 'slug': slug})

        return render(request, 'podmin/site/denied.html',
            {'return_url': return_url})

    episode.mothball()

    messages.success(request, 'Mothballed episode {0}.'.format(
        episode.title))

    return HttpResponseRedirect(reverse('podcast_show', kwargs={'slug': slug}))
