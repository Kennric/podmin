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
from podmin.models.helpers import *

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

class Episode(models.Model):

    """
    Episode model, defines a single episode of a podcast and methods to
    extract and set data about the episode.

    """
    podcast = models.ForeignKey('Podcast')
    created = models.DateTimeField('created', auto_now_add=True)
    updated = models.DateTimeField('updated', auto_now=True)
    published = models.DateTimeField('date published', null=True)
    mothballed = models.DateTimeField('date mothballed', null=True)

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    slug = AutoSlugField(populate_from='title', unique=True, default='')

    track_number = models.IntegerField('real episode number', blank=True,
                                       null=True)
    number = models.CharField('notional episode number', max_length=32,
                              blank=True, null=True)

    description = MarkdownField('short episode description',  blank=True,
                                null=True)

    buffer_audio = models.FileField('audio file',
                                    upload_to=get_audio_upload_path,
                                    storage=buffer_storage)
    audio = models.FileField('audio file')
    guid = models.CharField('published RSS GUID field',
                            unique=True, max_length=255)
    part = models.IntegerField(
        'part number of a multipart cast', blank=True, null=True)
    pub_date = models.DateTimeField('rss pubdate', blank=True, null=True)
    size = models.IntegerField('size in bytes', blank=True, null=True)
    length = models.CharField(
        'length in h,m,s format', max_length=32, blank=True, null=True)
    mime_type = models.CharField('audio mime type',
                                 default="application/octet-stream",
                                 max_length=32)
    active = models.BooleanField('active', default=1)
    tags = models.CharField(
        'comma separated list of tags', max_length=255, blank=True, null=True)
    show_notes = MarkdownField('show notes', blank=True, null=True)
    guests = MarkdownField('guests', blank=True, null=True)
    credits = MarkdownField('art and music credits',
                            blank=True, null=True)

    """
    image: For best results choose an attractive, original, and square JPEG
    (.jpg) or PNG (.png) image at a size of 1400x1400 pixels. Image will be
    scaled down to 50x50 pixels at smallest in iTunes. For reference see
    http://www.apple.com/itunes/podcasts/specs.html#metadata
    """
    image = models.ImageField('episode image')

    buffer_image = models.ImageField('image',
                                     upload_to=get_image_upload_path,
                                     storage=buffer_storage)

    image_type = models.CharField('image file type', max_length=16)

    # A URL that identifies a categorization taxonomy.
    categorization_domain = models.URLField(blank=True)
    summary = MarkdownField(blank=True)
    priority = models.DecimalField(max_digits=2, decimal_places=1,
                                   blank=True, null=True)
    block = models.BooleanField(default=False)

    @property
    def audio_url(self):
        audio_filename = os.path.basename(self.audio.name)
        return "%s/audio/%s" % (self.podcast.storage_url, audio_filename)

    @property
    def audio_filename(self):
        return os.path.basename(self.audio.name)

    @property
    def rss_image(self):
        filename = os.path.basename(self.image.name)
        file, ext = os.path.splitext(filename)
        rss_file = file + "_rss" + ext
        return "%s/img/%s" % (self.podcast.storage_url, rss_file)

    @property
    def itunes_image(self):
        filename = os.path.basename(self.image.name)
        file, ext = os.path.splitext(filename)
        rss_file = file + "_itunes" + ext
        return "%s/img/%s" % (self.podcast.storage_url, rss_file)

    @property
    def small_image(self):
        filename = os.path.basename(self.image.name)
        file, ext = os.path.splitext(filename)
        rss_file = file + "_small" + ext
        return "%s/img/%s" % (self.podcast.storage_url, rss_file)

    @property
    def medium_image(self):
        filename = os.path.basename(self.image.name)
        file, ext = os.path.splitext(filename)
        rss_file = file + "_medium" + ext
        return "%s/img/%s" % (self.podcast.storage_url, rss_file)

    @property
    def large_image(self):
        filename = os.path.basename(self.image.name)
        file, ext = os.path.splitext(filename)
        rss_file = file + "_large" + ext
        return "%s/img/%s" % (self.podcast.storage_url, rss_file)

    def __unicode__(self):
        return "%s: %s" % (self.podcast.title, self.title)

    class Meta:
        ordering = ["-pub_date, part"]
        get_latest_by = "pub_date"
        order_with_respect_to = 'podcast'
        unique_together = (("podcast", "number"), ("podcast", "track_number"))

    def get_absolute_url(self):
        return reverse("episode_show", kwargs={"eid": self.id,
                                               "slug": self.podcast.slug})

    def save(self, *args, **kwargs):

        """
        update the track number
        """

        # get the track number of the most recent episode for this
        # podcast
        if not self.track_number:
            try:
                last = Episode.objects.filter(podcast=self.podcast).latest()
                new_number = last.track_number + 1
            except:
                # maybe this is the first?
                new_number = 1

            self.track_number = new_number

        if not self.number:
            self.number = self.track_number

        logger.info("{0}: saving episode {1}".format(self.podcast.slug,
                                                     self.slug))
        super(Episode, self).save(*args, **kwargs)

    def post_process(self):
        """
        Take care of all those misc processing tasks that require the
        files to be in the buffer dir but should happen as soon as
        possible after saving the episode
        """
        logger.info(
            "{0}: post-processing episode {1}".format(self.podcast.slug,
                                                      self.slug))

        self.process_images()

        if self.podcast.tag_audio:
            self.tag()

    def tag(self):

        """
        If image or audio were added or updated, the new versions will
        be in the buffer at this point. Any manipulations we do on them
        should happen here, before the episode is published and the files
        get moved out to the world.
        """
        if self.buffer_audio:
            tagged = False

            logger.info("{0}: tagging file {1}".format(self.podcast,
                                                       self.buffer_audio.name))

            try:
                audio = PodcastAudio(self.buffer_audio.path)
                if self.podcast.tag_audio:
                    tagged = audio.tag_audio(self)

            except Exception as err:
                logger.info(
                    "{0}: error tagging: {1}".format(self.podcast, err))
                return False

        # no new audio, but is there a new image?
        if self.buffer_image:
            # do we need to tag it, or did we get it already?
            if not tagged:
                try:
                    audio = PodcastAudio(self.audio.path)
                    audio.tag_audio(self)
                except Exception as err:
                    logger.info(
                        "{0}: error tagging: {1}".format(self.podcast, err))
                    return False
        return True

    def process_images(self):
        # make all the image sizes for the episode
        try:
            image_sizer.make_image_sizes(self.buffer_image.path)
        except:
            pass

        return True

    def publish(self):
        """
        move files from the buffer location back into production, make this
        episode available for inclusion in the podcast feed
        """
        logger.info(
            "{0}: publishing episode {1}".format(self.podcast.slug, self.slug))

        if self.published and self.updated <= self.published:
            # This episode is already published, and hasn't been updated since
            pass
        else:
            self.published = datetime.now()

        """
        We assume that if you call this method, you want to publish now,
        not matter what. If pub_date is in the future, we need to
        set the pub_date to now to maintain rss validity.
        """
        if self.pub_date > datetime.now():
            self.pub_date = datetime.now()

        """
        Move the files.
        We're only working with buffered files here, if the buffer
        fields are empty, we have nothing to do
        """
        if self.buffer_audio:
            audio_source = self.buffer_audio.path
            audio_dest = os.path.join(settings.MEDIA_ROOT,
                                      self.buffer_audio.name)
            audio = PodcastAudio(audio_source)

            self.length = audio.duration()
            self.mime_type = audio.get_mimetype()[0]

            try:
                shutil.move(audio_source, audio_dest)
            except IOError as err:
                logger.error("{0}: publish failed for {1}: {2}".format(
                    self.podcast.slug, self.slug, err))
                return False

            self.audio = self.buffer_audio
            self.buffer_audio = None

        if self.buffer_image:

            image_file = os.path.basename(self.buffer_image.name)

            image_source = os.path.dirname(self.buffer_image.path) + "/"
            image_name, ext = os.path.splitext(image_file)

            image_dest = os.path.join(settings.MEDIA_ROOT,
                                      os.path.dirname(self.buffer_image.name),
                                      "")

            # if there is an image in the buffer, copy it at all its
            # associated resized versions to the storage dir using
            # glob

            try:
                image_glob = image_source + image_name + '*' + ext
                for image in glob.iglob(image_glob):
                    shutil.move(image, image_dest + os.path.basename(image))
            except:
                logger.error("{0}: publish failed for {1}: {2}".format(
                    self.podcast.slug, self.slug, err))
                return False

            self.image = self.buffer_image
            self.buffer_image = None

        """
        By definition a published episode is active, so make sure it is.
        """
        self.active = True
        self.save()

        return True

    def depublish(self):
        """
        move files from published location back into the buffer, make this
        episode unavailabe for inclusion in the podcast feed
        """
        logger.info("{0}: depublishing episode {1}".format(
            self.podcast.slug, self.slug))

        if self.audio:
            audio_source = self.audio.path
            audio_dest = os.path.join(settings.BUFFER_ROOT,
                                      self.audio.name)

            try:
                shutil.move(audio_source, audio_dest)
            except IOError as err:
                logger.error("{0}: depublish failed for {1}: {2}".format(
                    self.podcast.slug, self.slug, err))
                return False

            self.buffer_audio = self.audio
            self.audio = None

        if self.image:

            image_file = os.path.basename(self.image.name)

            image_source = os.path.dirname(self.image.path) + "/"
            image_name, ext = os.path.splitext(image_file)

            image_dest = os.path.join(settings.BUFFER_ROOT,
                                      os.path.dirname(self.image.name),
                                      "")

            # if there is an image in production, copy it and all its
            # associated resized versions back to the buffer dir using
            # glob
            try:
                image_glob = image_source + image_name + '*' + ext
                for image in glob.iglob(image_glob):
                    shutil.move(image, image_dest + os.path.basename(image))
            except:
                logger.error("{0}: depublish failed for {1}: {2}".format(
                    self.podcast.slug, self.slug, err))
                return False

            self.buffer_image = self.image
            self.image = None

        self.active = False

        self.published = None

        self.save()

        return True

    def transform_filename(self, filename):
        if not self.podcast.rename_files:
            return filename

        old, ext = os.path.splitext(filename)

        pattern = re.compile(r"\W", re.X)

        attributes = {'episode': self.slug,
                      'podcast': self.podcast.slug,
                      'number': self.number,
                      'track_number': self.track_number or 0,
                      'guid': pattern.sub("_", self.guid),
                      'part': self.part or 0,
                      'tags': pattern.sub("_",  self.tags or ""),
                      'org': pattern.sub("_", self.podcast.organization or ""),
                      'author': pattern.sub("_", self.podcast.author or ""),
                      'date': datetime.strftime(self.pub_date, "%Y%m%d")}

        new = "{0}{1}".format(
            self.podcast.file_rename_format.format(**attributes), ext)

        logger.info("{0}: episode {1}: saving {2} as {3}".format(
            self.podcast.slug, self.number, old, new))

        return new

    def mothball(self):

        logger.info("{0}: mothballing episode {1}".format(
            self.podcast.slug, self.slug))

        # make sure episode is unpublished and inactive
        if self.active or self.published:
            return False

        # make sure a new copy of the podcast mothball archive exists
        self.podcast.make_mothball()

        episode_dir = os.path.join(settings.ARCHIVE_ROOT, self.podcast.slug,
                                   "episodes")

        episode_filename = "{0}_{1}.json".format(
            self.id, datetime.strftime(self.pub_date, "%Y%m%d"))

        episode_file = os.path.join(episode_dir, episode_filename)

        # serialize current data
        episode = serializers.serialize('json', [self])

        # save serialized data to mothball_dir
        with open(episode_file, 'w+') as f:
            f.write(episode)

        # move files from buffer to mothball_dir
        audio_source = self.buffer_audio.path
        audio_dest = os.path.join(settings.ARCHIVE_ROOT,
                                  self.buffer_audio.name)

        try:
            shutil.move(audio_source, audio_dest)
        except IOError as err:
            logger.error("{0}: mothball failed for {1}: {2}".format(
                self.podcast.slug, self.slug, err))
            return False

        if self.buffer_image:
            image_file = os.path.basename(self.buffer_image.name)

            image_source = os.path.dirname(self.buffer_image.path) + "/"
            image_name, ext = os.path.splitext(image_file)

            image_dest = os.path.join(settings.ARCHIVE_ROOT,
                                      os.path.dirname(self.buffer_image.name),
                                      "")
            try:
                image_glob = image_source + image_name + '*' + ext
                for image in glob.iglob(image_glob):
                    shutil.move(image, image_dest + os.path.basename(image))
            except:
                logger.error("{0}: mothball failed for {1}: {2}".format(
                    self.podcast.slug, self.slug, err))
                return False

        # set mothballed property to current datetime

        self.mothballed = datetime.now()

        # set file fields to null
        self.buffer_image = None
        self.image = None
        self.buffer_audio = None
        self.audio = None
        self.save()
