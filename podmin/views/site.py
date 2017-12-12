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


def index(request):
    """
    front page view
    """
    podcasts = Podcast.objects.all()
    request_context = RequestContext(request)
    request_context.push({'podcasts': podcasts})

    return render(request, 'podmin/site/index.html', request_context)


def user_home(request):
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


def podmin_info(request):
    request_context = RequestContext(request)
    request_context.push({'static_dir': '/static/podcast/site'})
    return render(request, 'podmin/site/about.html', request_context)
