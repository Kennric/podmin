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
