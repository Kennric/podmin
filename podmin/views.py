# django stuff
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
#from django.core.servers.basehttp import FileWrapper

# podmin app stuff
from models import Podcast, Episode
from forms import PodcastForm, EpisodeForm

# python stuff
from datetime import datetime
import time
import logging
# import os

logger = logging.getLogger(__name__)

def testo(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug)
    podcast.publish_from_files()
    episodes = podcast.episode_set.all()

    return render(request, 'podmin/podcast/podcast.html',
                  {'podcast': podcast, 'episodes': episodes})

def user_role_check(req, slug):
    user = req.user

    manager = user.groups.filter(name="%s_managers" % slug).exists()
    editor = user.groups.filter(name="%s_editors" % slug).exists()
    webmaster = user.groups.filter(name="%s_webmasters" % slug).exists()

    return (user, manager, editor, webmaster)


def index(request):
    """
    front page view: display news, new episodes, featured
    episodes, contact links, etc
    login link
    """

    podcasts = Podcast.objects.all()
    context = {'podcasts': podcasts}
    return render(request, 'podmin/site/index.html', context)


def podcasts(request):
    """
    all podcasts
    list of all podcasts, brief description, feed links
    brief stats

    """

    podcasts = Podcast.objects.all()
    context = {'podcasts': podcasts}
    return render(request, 'podmin/site/podcasts.html', context)


def home(request):
    """
    my podcasts
    display all the podcasts owned by the current logged in
    user (or all for admin)
    if owner/admin
      action links - edit, promote, etc
    redirect here from login view
    """

    pass


def podcast(request, slug):
    """
    view podcast
    if admin/owner add:
      at top, general stats/graphs
      action links (delete, edit, promote) per episode
      and add episode link at top
    otherwise, podcast homepage - get template name from podcast slug
    see all the episodes
    play button
    subscribe links
    share links
    """
    user, manager, editor, webmaster = user_role_check(request, slug)

    podcast = get_object_or_404(Podcast, slug=slug)
    episodes = podcast.episode_set.all()

    return render(request, 'podmin/podcast/podcast.html',
                  {'podcast': podcast, 'episodes': episodes})


@login_required
def edit_podcast(request, slug):
    """
    edit podcast
    user-editable options for a specific podcast
    make sure user is superadmin or podcast owner
    advanced options - directory to upload to for
    auto-processing

    """
    user, manager, editor, webmaster = user_role_check(request, slug)

    if not manager and not user.is_superuser:
        message = "I'm sorry %s, I'm afraid I can't let you edit %s" % (user,
                                                                        slug)

        return render(request, 'podmin/site/denied.html', {'message': message})

    podcast = Podcast.objects.get(slug=slug)
    if request.method == 'POST':
        form = PodcastForm(request.POST, request.FILES, instance=podcast)
        if form.is_valid():
            podcast = form.save()
            return HttpResponseRedirect(reverse('podcast_show',
                                                kwargs={'slug': slug}))


    form = PodcastForm(instance=podcast)

    context = {'form': form,
               'slug': slug,
               'manager': manager,
               'editor': editor,
               'webmaster': webmaster,
               'podcast': podcast}

    return render(request, 'podmin/podcast/podcast_edit.html', context)


@login_required
def new_podcast(request):
    """
    new podcast
    make a new one

    """

    form = PodcastForm()
    if request.method == 'POST':
        form = PodcastForm(request.POST, request.FILES)
        if form.is_valid():
            podcast = form.save()
            return HttpResponseRedirect(reverse(
                'podcast_show', kwargs={
                    'slug': podcast.slug}))

    return render(request, 'podmin/podcast/podcast_edit.html',
                  {'form': form})


@login_required
def delete_podcast(request, slug):
    user, manager, editor, webmaster = user_role_check(request, slug)
    if not manager and not user.is_superuser:
        message = "I'm sorry %s, I'm afraid I can't let you delete %s" % (user,
                                                                          slug)
        return render(request, 'podmin/site/denied.html', {'message': message})

    podcast = get_object_or_404(Podcast, slug=slug)
    podcast.delete()
    return HttpResponseRedirect(reverse('index'))


def episode(request, eid, slug):
    """
    view episode
    """
    episode = get_object_or_404(Episode, pk=eid)

    return render(request, 'podmin/episode/episode.html', {'episode': episode})


@login_required
def edit_episode(request, eid, slug):

    user, manager, editor, webmaster = user_role_check(request, slug)

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
            episode.save()

            if episode.podcast.rename_files:
                episode.rename_audio()
                episode.rename_image()

            episode.process_images()

            if episode.podcast.tag_audio:
                episode.tag()

            episode.podcast.publish()

            return HttpResponseRedirect(reverse(
                'episode_show',
                kwargs={'eid': episode.id, 'slug': slug}))

    else:
        form = EpisodeForm(instance=episode)

    #form.fields['filename'].widget.attrs['readonly'] = True

    return render(request,
                  'podmin/episode/episode_edit.html',
                  {'form': form, 'episode': episode})


@login_required
def new_episode(request, slug):

    user, manager, editor, webmaster = user_role_check(request, slug)

    podcast = get_object_or_404(Podcast, slug=slug)

    guid = "%s%s" % (slug, time.time())

    # get the next episode number for this podcast
    #episode_number = podcast.episode_set.latest().number + 1

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
            episode.save()

            if episode.podcast.rename_files:
                episode.rename_audio()
                episode.rename_image()

            episode.process_images()

            if episode.podcast.tag_audio:
                episode.tag()

            episode.podcast.publish()

            return HttpResponseRedirect(reverse(
                'episode_show',
                kwargs={'eid': episode.id, 'slug': slug}))

    return render(request, 'podmin/episode/episode_edit.html',
                  {'form': form, 'podcast': podcast})


@login_required
def delete_episode(request, eid, slug):

    user, manager, editor, webmaster = user_role_check(request, slug)

    if not manager and not user.is_superuser:
        message = "I'm sorry %s, I'm afraid I can't let you delete episode %s" % (
            user, eid)

        return render(request, 'podmin/site/denied.html', {'message': message})

    episode = get_object_or_404(Episode, id=eid)
    episode.delete()
    return HttpResponseRedirect(reverse('podcast_show', kwargs={'slug': slug}))


def podmin_info(request):

    return render(request, 'podmin/site/about.html',
                  {'static_dir': '/static/podcast/site'})

"""

def audio_buffer(request, filename):

    #Send a file through Django without loading the whole file into
    #memory at once. The FileWrapper will turn the file object into an
    #iterator for chunks of 8KB.

    filename = __file__ # Select your file here.
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(filename)
    return response

def image_buffer(request):

    #Send a file through Django without loading the whole file into
    #memory at once. The FileWrapper will turn the file object into an
    #iterator for chunks of 8KB.

    filename = __file__ # Select your file here.
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(filename)
    return response

"""


def login_user(request):
    """
    */login*

    This view will display a login page if GET'd, or attempt login if POST'd.
    If the GET parameter logout is set, it will change the message on the page
    to indicate a successful logout.

    If a user is already logged in and tries to access this page, they will be
    redirected to /entry.
    """

    state = "Please log in."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if request.POST.get('next'):
                    return HttpResponseRedirect(request.POST.get('next'))
                else:
                    return HttpResponseRedirect('/')
            else:
                state = "Your account is not active."
        else:
            next = request.POST.get('next')
            state = "Invalid username or password."
    else:
        next = request.GET.get('next')

    if request.GET.get('logout', False):
        state = "Logged out successfully!"

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('/'))

    return render(request, 'auth.html', {
        'state': state, 'username': username, 'next': next, 'title': 'Log In'})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('{}?logout=true'.format(reverse('login')))
