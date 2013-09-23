# django stuff
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

# podmin app stuff
from podmin.models import Podcast, Episode
from podmin.forms import PodcastForm, EpisodeForm

# python stuff
from datetime import datetime, timedelta, date
from subprocess import check_output


def index(request):
    """
    front page view: display news, new episodes, featured
    episodes, contact links, etc
    login link
    """
    podcasts = Podcast.objects.all()
    context = {'podcasts': podcasts}
    return render(request, 'podmin/index.html', context)


def podcasts(request):
    """
    all podcasts
    list of all podcasts, brief description, feed links
    brief stats

    """
    podcasts = Podcast.objects.all()
    context = {'podcasts': podcasts}
    return render(request, 'podmin/podcasts.html', context) 


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



def podcast(request, pid):
    """
    view podcast
    if admin/owner add:
      at top, general stats/graphs
      action links (delete, edit, promote) per episode
      and add episode link at top
    otherwise, podcast homepage - get template name from podcast shortname
    see all the episodes
    play button
    subscribe links
    share links
    """
    podcast = get_object_or_404(Podcast, pk=pid)
    episodes = podcast.episode_set.all()
    return render(request, 'podmin/podcast.html',
                  {'podcast': podcast, 'episodes': episodes})


def edit_podcast(request, pid):
    """
    edit podcast
    user-editable options for a specific podcast
    make sure user is superadmin or podcast owner
    advanced options - directory to upload to for
    auto-processing

    """

    podcast = Podcast.objects.get(pk=pid)
    if request.method == 'POST':
        form = PodcastForm(request.POST, instance=podcast)
        if form.is_valid():
            podcast = form.save()
            return HttpResponseRedirect('/podcast/' + str(podcast.id))

    form = PodcastForm(instance=podcast)

    return render(request, 'podmin/podcast_edit.html',
                  {'form': form, 'pid': pid})


def new_podcast(request):
    """
    new podcast
    make a new one

    """

    form = PodcastForm()
    if request.method == 'POST':
        form = PodcastForm(request.POST)
        if form.is_valid():
            podcast = form.save()
            return HttpResponseRedirect('/podcast/' + str(podcast.id))

    return render(request, 'podmin/podcast_edit.html',
                  {'form': form})


def episode(request, eid):
    """
    view episode
    specific episode page
    play, share, etc buttons
    """
    episode = get_object_or_404(Episode, pk=eid)
    return render(request, 'podmin/episode.html',
                  {'episode': episode})


def edit_episode(request, eid):
    episode = Episode.objects.get(pk=eid)
    if request.method == 'POST':
        form = EpisodeForm(request.POST, request.FILES, instance=episode) 
        
        if form.is_valid():
            episode = form.save(commit=False)

            if form.cleaned_data['upload_file']:
                episode = handle_file(episode, form, request)

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

    return render(request, 'podmin/episode_edit.html',
                  {'form': form, 'episode': episode})


def new_episode(request, pid):
    podcast = get_object_or_404(Podcast, pk=pid)
    form = EpisodeForm()

    if request.method == 'POST':
        form = EpisodeForm(request.POST, request.FILES)
        if form.is_valid():
            episode = form.save(commit=False)
            episode.podcast = podcast

            if form.cleaned_data['upload_file']:
                episode = handle_file(episode, form, request)

            episode.save()

            if (form.cleaned_data['pub_date'] <= datetime.now()
                and form.cleaned_data['active']):

                published = episode.podcast.publish()
                if published is not True:
                    messages.error(request,
                                   "Podcast not published: " + published)

            return HttpResponseRedirect('/episode/' + str(episode.id))

    return render(request, 'podmin/episode_edit.html',
                  {'form': form, 'podcast': podcast})


def handle_file(episode, form, request):       
    uploaded_file = form.cleaned_data['upload_file']  
    upload_filename = uploaded_file.name
    episode.filename = upload_filename
    
    episode.save_to_tmp(uploaded_file)

    path = episode.podcast.tmp_dir + '/' + episode.filename
    episode.length = check_output(["soxi", "-d", path]).split('.')[0]
    episode.size = uploaded_file.size

    if form.cleaned_data['rename_file']:
        renamed = episode.rename_file()
        if renamed is not True:
            messages.error(request,
                           "Problem renaming file: " + renamed)
        else:
            messages.success(request,
                             "File renamed to " + episode.filename)

    if form.cleaned_data['tag_audio']:
        tagged = episode.setTags()
        if tagged is not True:
            messages.warning(request,
                             "Problem tagging audio: " + tagged)
        else:
            messages.success(request, "Audio tagged successfully")

    return episode
