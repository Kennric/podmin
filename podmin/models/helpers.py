# django stuff
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.core.files.storage import FileSystemStorage
from django.core import serializers
from django.http import HttpRequest

# django contrib stuff
from autoslug import AutoSlugField
from django_markdown.models import MarkdownField
from django.contrib.sites.models import Site

# podmin app stuff
#import podmin
from podmin.util.podcast_audio import PodcastAudio
from podmin.util import image_sizer
from podmin.util.file_import import FileImporter
from podmin.constants import *

# python stuff
import os
import shutil
from datetime import timedelta, datetime
import glob
import time
import logging
import re
from urlparse import urlparse

logger = logging.getLogger(__name__)

buffer_storage = FileSystemStorage(location=settings.BUFFER_ROOT)


def get_default_image():
    return os.path.join(settings.STATIC_ROOT, 'img', 'default_podcast.png')


def get_image_upload_path(instance, filename):
    # if the podcast has rename_files set, transform the name here

    filename = instance.transform_filename(filename)

    if instance.__class__ is Episode:
        return os.path.join(instance.podcast.slug, "img", filename)

    if instance.__class__ is Podcast:
        return os.path.join(instance.slug, "img", filename)


def get_audio_upload_path(instance, filename):

    filename = instance.transform_filename(filename)

    if instance.__class__ is Episode:
        return os.path.join(instance.podcast.slug, "audio", filename)

    if instance.__class__ is Podcast:
        return os.path.join(instance.slug, "audio", filename)
