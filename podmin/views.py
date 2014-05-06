# django stuff
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

# podmin app stuff
from models import Podcast, Episode
from forms import PodcastForm, EpisodeForm

# python stuff
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def index(request, subsite=''):
    """
    front page view: display news, new episodes, featured
    episodes, contact links, etc
    login link
    """
    if subsite != '':
        subsite = subsite + '/'

    podcasts = Podcast.objects.all()
    context = {'podcasts': podcasts, 'subsite': subsite}
    return render(request, 'podmin/site/index.html', context)


def podcasts(request, subsite=''):
    """
    all podcasts
    list of all podcasts, brief description, feed links
    brief stats

    """
    if subsite != '':
        subsite = subsite + '/'
    
    podcasts = Podcast.objects.all()
    context = {'podcasts': podcasts, 'subsite': subsite}
    return render(request, 'podmin/site/podcasts.html', context)


def home(request, subsite=''):
    """
    my podcasts
    display all the podcasts owned by the current logged in
    user (or all for admin)
    if owner/admin
      action links - edit, promote, etc
    redirect here from login view
    """
    if subsite != '':
        subsite = subsite + '/'
    pass


def podcast(request, slug, subsite=''):
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
    if subsite != '':
        subsite = subsite + '/'
    
    podcast = get_object_or_404(Podcast, slug=slug)
    episodes = podcast.episode_set.all()

    static_dir, template_dir = podcast.get_theme()

    return render(request, 'podmin/podcast/%s/podcast.html' % template_dir,
                  {'podcast': podcast, 'episodes': episodes,
                   'static_dir': static_dir})


def edit_podcast(request, slug, subsite=''):
    """
    edit podcast
    user-editable options for a specific podcast
    make sure user is superadmin or podcast owner
    advanced options - directory to upload to for
    auto-processing

    """
    if subsite != '':
        subsite = subsite + '/'

    podcast = Podcast.objects.get(slug=slug)
    if request.method == 'POST':
        form = PodcastForm(request.POST, request.FILES, instance=podcast)
        if form.is_valid():
            podcast = form.save()
            return HttpResponseRedirect('/podcast/' + str(podcast.slug))

    form = PodcastForm(instance=podcast)

    static_dir, template_dir = podcast.get_theme()

    return render(request,
                  'podmin/podcast/%s/podcast_edit.html' % template_dir,
                  {'form': form, 'slug': slug, 'static_dir': static_dir})


def new_podcast(request, subsite=''):
    """
    new podcast
    make a new one

    """
    if subsite != '':
        subsite = subsite + '/'

    form = PodcastForm()
    if request.method == 'POST':
        form = PodcastForm(request.POST, request.FILES)
        if form.is_valid():
            podcast = form.save()
            return HttpResponseRedirect('/podcast/' + str(podcast.id))

    return render(request, 'podmin/podcast/site/podcast_edit.html',
                  {'form': form, 'static_dir': '/static/podcast/site'})


def episode(request, eid, subsite=''):
    """
    view episode
    specific episode page
    play, share, etc buttons
    """
    if subsite != '':
        subsite = subsite + '/'
    
    episode = get_object_or_404(Episode, pk=eid)

    static_dir, template_dir = episode.podcast.get_theme()

    return render(request, 'podmin/podcast/%s/episode.html' % template_dir,
                  {'episode': episode, 'static_dir': static_dir})


def edit_episode(request, eid, subsite=''):
    if subsite != '':
        subsite = subsite + '/'
    
    episode = Episode.objects.get(pk=eid)
    if request.method == 'POST':
        form = EpisodeForm(request.POST, request.FILES, instance=episode)

        if form.is_valid():
            episode = form.save(commit=False)

            if form.cleaned_data['upload_file']:
                episode.handle_uploaded_audio(form, messages, request)

            episode.save()

            if (form.cleaned_data['pub_date'] <= datetime.now()
                    and form.cleaned_data['active']):

                published = episode.podcast.publish()
                if published is not True:
                    messages.error(request,
                                   "Podcast not published: " + published)

            return HttpResponseRedirect('/episode/' + str(episode.id))

    else:
        form = EpisodeForm(instance=episode)

    form.fields['filename'].widget.attrs['readonly'] = True

    static_dir, template_dir = episode.podcast.get_theme()

    return render(request,
                  'podmin/podcast/%s/episode_edit.html' % template_dir,
                  {'form': form, 'episode': episode,
                   'static_dir': static_dir})


def new_episode(request, slug=None, subsite=''):
    if subsite != '':
        subsite = subsite + '/'
    
    podcast = get_object_or_404(Podcast, slug=slug)
    form = EpisodeForm()

    if request.method == 'POST':
        form = EpisodeForm(request.POST, request.FILES)
        if form.is_valid():
            episode = form.save(commit=False)
            episode.podcast = podcast

            if form.cleaned_data['upload_file']:
                episode.handle_uploaded_audio(form, messages, request)

            episode.save()

            if (form.cleaned_data['pub_date'] <= datetime.now()
                    and form.cleaned_data['active']):

                published = episode.podcast.publish()
                if published is not True:
                    messages.error(request,
                                   "Podcast not published: " + published)

            return HttpResponseRedirect('/episode/' + str(episode.id))

    return render(request, 'podmin/podcast/site/episode_edit.html',
                  {'form': form, 'podcast': podcast,
                   'static_dir': '/static/podcast/site'})
