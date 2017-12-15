# django stuff
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.servers.basehttp import FileWrapper

# podmin app stuff
from podmin.models import Episode

# python stuff
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

    wrapper = FileWrapper(open(filepath))

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

    wrapper = FileWrapper(open(buffer_path))
    response = HttpResponse(wrapper, content_type=episode.image_type)
    response['Content-Length'] = os.path.getsize(buffer_path)
    return response
