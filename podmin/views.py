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
from models import Podcast, Episode
from forms import PodcastForm, EpisodeForm

# python stuff
import time
import logging
import os

logger = logging.getLogger(__name__)


def user_role_check(req, slug):
    """
    Check what roles the user has relative to a particular podcast
    """
    user = req.user

    manager = user.groups.filter(name="%s_managers" % slug).exists()
    editor = user.groups.filter(name="%s_editors" % slug).exists()
    webmaster = user.groups.filter(name="%s_webmasters" % slug).exists()

    return (user, manager, editor, webmaster)


def index(request):
    """
    front page view
    """
    podcasts = Podcast.objects.all()
    request_context = RequestContext(request)
    request_context.push({'podcasts': podcasts})

    return render(request, 'podmin/site/index.html', request_context)


def podcasts(request):
    """
    all podcasts

    """
    podcasts = Podcast.objects.all()
    request_context = RequestContext(request)
    request_context.push({'podcasts': podcasts})

    return render(request, 'podmin/site/podcasts.html', request_context)


def home(request):
    """
    List podcasts for which the user has some role
    """
    slug_list = []
    for group in request.user.groups.all():
        slug_list.append(group.name.split('_')[0])

    slugs = set(slug_list)
    podcasts = Podcast.objects.filter(slug__in=slugs)

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

    messages.error(request, 'ERROR Testing!')

    request_context = RequestContext(request)
    request_context.push({'podcast': podcast, 'episodes': episodes,
                          'manager': manager, 'editor': editor,
                          'webmaster': webmaster, 'messages': messages})

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
        messages.error(request, 'Nope!')

        return render(request, 'podmin/site/denied.html', {'message': message})

    podcast = Podcast.objects.get(slug=slug)
    if request.method == 'POST':
        form = PodcastForm(request.POST, request.FILES, instance=podcast)
        if form.is_valid():
            messages.success(request, '{0} updated.'.format(podcast.title))
            podcast = form.save()
            podcast.publish()
            return HttpResponseRedirect(reverse('podcast_show',
                                                kwargs={'slug': slug}))

    form = PodcastForm(instance=podcast)

    form.fields['slug'].widget.attrs['readonly'] = True

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

        return render(request, 'podmin/site/denied.html', {'message': message})

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

            return HttpResponseRedirect(reverse(
                'podcast_show', kwargs={
                    'slug': podcast.slug}))

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
        return render(request, 'podmin/site/denied.html', {'message': message})

    podcast = get_object_or_404(Podcast, slug=slug)

    if request.method == 'POST':
        if request.POST.get('confirmed', False):

            podcast.delete()
            return HttpResponseRedirect(reverse('index'))

    return render(request, 'podmin/podcast/podcast_delete.html',
                  {'podcast': podcast})


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

            return render(request,
                          'podmin/site/denied.html', {'message': message})

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

            return render(request,
                          'podmin/site/denied.html', {'message': message})

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

            return render(request, 'podmin/site/denied.html',
                          {'message': message})

    episode = get_object_or_404(Episode, id=eid)

    if request.method == 'POST':
        if request.POST.get('confirmed', False):
            episode.delete()
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

            return render(request, 'podmin/site/denied.html',
                          {'message': message})

    episode = get_object_or_404(Episode, id=eid)

    episode.depublish()
    episode.podcast.publish_feed()

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

            return render(request, 'podmin/site/denied.html',
                          {'message': message})

    episode = get_object_or_404(Episode, id=eid)

    episode.publish()
    episode.podcast.publish_feed()

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

            return render(request, 'podmin/site/denied.html',
                          {'message': message})

    episode = get_object_or_404(Episode, id=eid)

    if episode.active or episode.published:
        message = """I'm sorry {0}, before you can mothball an episode, it must
                     be inactive and not published.""".format(user)

        return render(request, 'podmin/site/denied.html', {'message': message})

    episode.mothball()

    return HttpResponseRedirect(reverse('podcast_show', kwargs={'slug': slug}))


def podmin_info(request):
    request_context = RequestContext(request)
    request_context.push({'static_dir': '/static/podcast/site'})
    return render(request, 'podmin/site/about.html', request_context)


def audio_buffer(request, eid, slug):
    """
    Send a file through Django without loading the whole file into
    memory at once. The FileWrapper will turn the file object into an
    iterator for chunks of 8KB.
    """

    episode = get_object_or_404(Episode, id=eid)
    filepath = episode.buffer_audio.path
    filename = os.path.basename(episode.buffer_audio.name)
    content_type = episode.mime_type

    wrapper = FileWrapper(file(filepath))

    response = HttpResponse(wrapper, content_type=content_type)
    response['Content-Length'] = os.path.getsize(filepath)
    response['Content-Disposition'] = "attachment; filename={0}".format(
        filename)

    return response


def image_buffer(request, eid, slug, size):
    """
    Send a file through Django without loading the whole file into
    memory at once. The FileWrapper will turn the file object into an
    iterator for chunks of 8KB.
    """
    episode = get_object_or_404(Episode, id=eid)

    path, filename = os.path.split(episode.buffer_image.path)
    name, ext = os.path.splitext(filename)
    image_name = "{0}_{1}{2}".format(name, size, ext)
    buffer_path = os.path.join(path, image_name)

    wrapper = FileWrapper(file(buffer_path))
    response = HttpResponse(wrapper, content_type=episode.image_type)
    response['Content-Length'] = os.path.getsize(buffer_path)
    return response


def login_user(request):
    """
    Log a user in, or display the login form
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
        return HttpResponseRedirect(reverse(next))

    return render(request, 'registration/login.html', {
        'state': state, 'username': username, 'next': next, 'title': 'Log In'})


def logout_user(request):
    """
    Log a user out
    """
    logout(request)
    return HttpResponseRedirect('{}?logout=true'.format(reverse('login')))
