from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from podmin.models import Podcast, Episode
from podmin.forms import PodcastForm, EpisodeForm

# front page view: display news, new episodes, featured
# episodes, contact links, etc
# login link


def index(request):
    """
    get promoted podcasts and episodes
    
    """
    podcasts = Podcast.objects.all()
    context = {'podcasts': podcasts}
    return render(request, 'podmin/index.html', context)

# all podcasts
# list of all podcasts, brief description, feed links
# brief stats

def podcasts(request):
    """
    get all podcasts
    get podcasts stats (???)
    """
    podcasts = Podcast.objects.all()
    context = {'podcasts': podcasts}
    return render(request, 'podmin/podcasts.html', context) 

# my podcasts
# display all the podcasts owned by the current logged in 
# user (or all for admin)
# if owner/admin
#   action links - edit, promote, etc
# redirect here from login view

def home(request):
    """
    get current user
    get user's podcasts (all if admin)
    get stats for user (???)
    """
    pass


# view podcast
# if admin/owner add:
#   at top, general stats/graphs
#   action links (delete, edit, promote) per episode
#   and add episode link at top
# otherwise, podcast homepage - get template name from podcast shortname
# see all the episodes
# play button
# subscribe links
# share links
def podcast(request, pid):
    """
    get this podcast
    """
    podcast = get_object_or_404(Podcast, pk=pid)
    episodes = podcast.episode_set.all()
    return render(request, 'podmin/podcast.html',
                  {'podcast': podcast, 'episodes': episodes})


# edit podcast
# user-editable options for a specific podcast
# make sure user is superadmin or podcast owner
# advanced options - directory to upload to for
# auto-processing
def edit_podcast(request, pid=None):
    """
    if pid is none, make form for new podcast
    else make form to edit existing

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


# new podcast
# make a new one
def new_podcast(request):
    """
    if pid is none, make form for new podcast
    else make form to edit existing

    """

    form = PodcastForm()
    if request.method == 'POST':
        form = PodcastForm(request.POST)
        if form.is_valid():
            podcast = form.save()
            return HttpResponseRedirect('/podcast/' + str(podcast.id))

    return render(request, 'podmin/podcast_edit.html',
                  {'form': form})


# view episode
# specific episode page
# play, share, etc buttons
def episode(request, eid):
    episode = get_object_or_404(Episode, pk=eid)
    return render(request, 'podmin/episode.html',
                  {'episode': episode})


# add episode if pid but nor eid
# upload new file (drag and drop?)
# if eid edit existing episode
def edit_episode(request,eid):
    episode = Episode.objects.get(pk=eid)
    if request.method == 'POST':
        form = EpisodeForm(request.POST, instance=episode)
        if form.is_valid():
            episode = form.save()
            return HttpResponseRedirect('/episode/' + str(episode.id))

    form = EpisodeForm(instance=episode)

    return render(request, 'podmin/episode_edit.html',
                  {'form': form, 'eid': eid})


def new_episode(request,pid):
    podcast = get_object_or_404(Podcast, pk=pid)
    form = EpisodeForm()
    if request.method == 'POST':
        form = EpisodeForm(request.POST)
        if form.is_valid():
            episode = form.save(commit=False)
            episode.podcast = podcast
            episode.save()
            return HttpResponseRedirect('/episode/' + str(episode.id))

    return render(request, 'podmin/episode_edit.html',
                  {'form': form})
