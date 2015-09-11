# django stuff
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest
from django.core.files import File

# django contrib stuff
from autoslug import AutoSlugField

# podmin app stuff
import podmin
from util.podcast_audio import PodcastAudio
from util import image_sizer
from util.file_import import FileImporter

from constants import *

# python stuff
import os
from datetime import datetime, timedelta, date
import glob
import time
import shutil

"""
import logging
import re
"""

# audio tagging/processing stuff

from subprocess import check_output
"""
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
"""

buffer_storage = FileSystemStorage(location=settings.BUFFER_ROOT)


def get_default_image():
    return os.path.join(settings.STATIC_ROOT, 'img', 'default_podcast.png')

def get_image_upload_path(instance, filename):
    if instance.__class__ is Episode:
        return os.path.join(instance.podcast.slug, "img", filename)

    if instance.__class__ is Podcast:
        return os.path.join(instance.slug, "img", filename)


def get_audio_upload_path(instance, filename):
    if instance.__class__ is Episode:
        return os.path.join(instance.podcast.slug, "audio", filename)

    if instance.__class__ is Podcast:
        return os.path.join(instance.slug, "audio", filename)


class Category(models.Model):

    """
    Category model, stores the tree of iTunes categories

    """
    itunes = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __unicode__(self):
        if self.parent:
            return "%s / %s" % (self.parent, self.name)
        else:
            return self.name

    class Meta:
        ordering = ["name"]
        order_with_respect_to = 'parent'


class Podcast(models.Model):

    """
    Podcast model defines a podcast stream and methods to publish the RSS file

    """
    # standard things
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, default=1)
    slug = models.SlugField(unique=True)
    credits = models.TextField('art and music credits', blank=True, null=True)
    created = models.DateTimeField('created', auto_now_add=True,
                                   editable=False)
    published = models.DateTimeField('last published', blank=True, null=True)
    updated = models.DateTimeField('updated', auto_now=True)
    website = models.URLField('podcast website', blank=True, null=True)
    frequency = models.CharField(max_length=10,
                                 choices=FREQUENCY_CHOICES,
                                 blank=True, default='never')
    active = models.BooleanField(default=True)
    feed_format = models.CharField('feed format',
                                   max_length=16, default='rss',
                                   choices=FEED_TYPE_CHOICES)
    # directories
    pub_url = models.URLField('base publication url', blank=True,
                              default="")
    pub_dir = models.CharField('rss publication path', max_length=255,
                               blank=True, default="")
    storage_dir = models.CharField('storage base dir', max_length=255,
                                   blank=True, default="")
    storage_url = models.URLField('storage base url', blank=True,
                                  default="")
    tmp_dir = models.CharField('path to temporary processing location',
                               max_length=255, default="/tmp")

    # things related to importing from the filesystem
    last_import = models.DateTimeField('last import', blank=True, null=True)
    combine_segments = models.BooleanField(default=False)
    publish_segments = models.BooleanField(default=False)
    up_dir = models.CharField('path to the upload location', max_length=255)
    cleaner = models.CharField('file cleaner function name',
                               max_length=255, default='default')

    # general file manipulation things
    rename_files = models.BooleanField(default=False)
    tag_audio = models.BooleanField(default=False)

    # RSS specific
    organization = models.CharField(max_length=255, default='')
    station = models.CharField('broadcasting station name',
                               max_length=16, blank=True)
    description = models.TextField(blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    contact = models.EmailField(max_length=255, blank=True, null=True)
    image = models.ImageField('cover art', upload_to=get_image_upload_path)
    copyright = models.CharField(max_length=255, blank=True, null=True)
    license = models.CharField('license',
                               max_length=255, blank=True, null=True,
                               choices=LICENSE_CHOICES)
    copyright_url = models.TextField('copyright url', blank=True, null=True)
    language = models.CharField(max_length=8, choices=LANGUAGE_CHOICES)
    feedburner_url = models.URLField('FeedBurner URL', blank=True)
    ttl = models.IntegerField('minutes this feed can be cached', default=1440)
    tags = models.CharField('comma separated list of tags',
                            max_length=255, blank=True, null=True)
    max_age = models.IntegerField('days to keep an episode', default=365)
    editor_email = models.EmailField('editor email', blank=True)
    webmaster_email = models.EmailField('webmaster email', blank=True)

    # itunes specific

    categorization_domain = models.URLField(blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    explicit = models.CharField(max_length=255, default='No',
                                choices=EXPLICIT_CHOICES, blank=True)
    block = models.BooleanField(default=False)

    itunes_categories = models.ManyToManyField(Category, blank=True)

    """
    The show's new URL feed if changing the URL of the current show feed.
    Must continue old feed for at least two weeks and write a 301 redirect
    for old feed.

    """
    redirect = models.URLField(blank=True)
    keywords = models.CharField(max_length=255, blank=True)
    """
    itunes: Fill this out after saving this show and at least one episode.
    URL should look like
    "http://phobos.apple.com/WebObjects/MZStore.woa/wa/
                                                viewPodcast?id=000000000".
    See https://github.com/jefftriplett/django-podcast for more.

    """
    itunes_url = models.URLField('iTunes Store URL', blank=True)

    """
    This constant defines the groups and permissions that will be created
    for each podcast when it is created
    manage: edit podcast itself (Podcast model parameters)
    edit: add and edit episodes
    web: edit show notes, episode picture, etc
    """

    GROUP_PERMS = {'managers': 'manage', 'editors': 'edit',
                   'webmasters': 'web', 'all': 'view'}

    def __unicode__(self):
        return self.title

    @property
    def generator(self):
        return podmin.get_name() + " " + podmin.get_version()

    @property
    def rss_image(self):
        filename = os.path.basename(self.image.name)
        file, ext = os.path.splitext(filename)
        rss_file = file + "_rss" + ext
        return os.path.join(self.storage_url, "img", rss_file)

    @property
    def itunes_image(self):
        filename = os.path.basename(self.image.name)
        file, ext = os.path.splitext(filename)
        rss_file = file + "_itunes" + ext
        return os.path.join(self.storage_url, "img", rss_file)

    @property
    def small_image(self):
        filename = os.path.basename(self.image.name)
        file, ext = os.path.splitext(filename)
        rss_file = file + "_small" + ext
        return os.path.join(self.storage_url, "img", rss_file)

    @property
    def medium_image(self):
        filename = os.path.basename(self.image.name)
        file, ext = os.path.splitext(filename)
        rss_file = file + "_medium" + ext
        return os.path.join(self.storage_url, "img", rss_file)

    @property
    def large_image(self):
        filename = os.path.basename(self.image.name)
        file, ext = os.path.splitext(filename)
        rss_file = file + "_large" + ext
        return os.path.join(self.storage_url, "img", rss_file)

    def save(self, *args, **kwargs):
        """
        set these urls to local media urls if not specified.
        """

        if not self.pub_url:
            self.pub_url = "%s%s" % (settings.MEDIA_URL, self.slug)

        if not self.storage_url:
            self.storage_url = "%s%s" % (settings.MEDIA_URL, self.slug)

        image_pub_dir = os.path.join(settings.MEDIA_ROOT, self.slug, "img")
        audio_pub_dir = os.path.join(settings.MEDIA_ROOT, self.slug, "audio")

        """
        make sure pub dirs exist
        """
        try:
            os.makedirs(image_pub_dir)
        except:
            pass

        try:
            os.makedirs(audio_pub_dir)
        except:
            pass

        super(Podcast, self).save(*args, **kwargs)

    def publish(self):
        self.publish_episodes()
        self.publish_feed()
        self.expire_episodes()

        return True

    def publish_episodes(self):

        # publish episodes that are ripe
        expired_date = date.today() - timedelta(days=self.max_age)

        episodes = self.episode_set.filter(pub_date__gte=expired_date,
                                           active=True)

        for episode in episodes:
            episode.publish()

    def publish_feed(self):
        """
        Pull the feed from the feed generator, store it in the
        pub_dir.

        """

        if self.feed_format == 'atom':
            feed_filename = 'atom.xml'
            url_path = "/{0}/atom/".format(self.slug)

        elif self.feed_format == 'rss':
            feed_filename = 'rss.xml'
            url_path = "/{0}/rss/".format(self.slug)

        view, args, kwargs = resolve(url_path)
        request = HttpRequest()

        feed_content = view(request, *args, **kwargs).content

        feed_file = os.path.join(settings.MEDIA_ROOT, self.slug, feed_filename)

        try:
            f = open(feed_file, 'w')
            f.write(feed_content)
            f.close
        except IOError as err:
            return '; '.join(err.messages)

        self.published = datetime.now()

        self.save()

    def expire_episodes(self):
        """
        Expire old episodes by setting active = False where the pubDate
        plus the given delta is less than today's date

        """
        expired_date = date.today() - timedelta(days=self.max_age)

        self.episode_set.filter(pub_date__lte=expired_date,
                                active=True).update(active=False,
                                                    published=None)

    def publish_from_files(self):
        """
        Wrapper method to check for new files on disk and publish
        them if found
        """

        # if the up_dir is not set, what are we even doing here?
        if not self.up_dir:
            print("up_dir not set!")
            return False

        # if the up_dir isn't a directory, this is going nowhere
        if not os.path.isdir(self.up_dir):
            print("up_dir isn't a dir!")
            return False

        try:
            importer = FileImporter(self)
        except:
            # TODO handle this
            print("importer failed to init!")

        status = importer.scan()

        if not status:
            # TODO handle this
            print("no files!")

        try:
            new_files = importer.fetch()
        except:
            # TODO handle this
            return False

        try:
            new_files = importer.clean()
        except:
            # TODO handle this
            return False

        if self.combine_segments:
            try:
                new_files = importer.combine()
            except:
                # TODO handle this
                print("whoops!")
                return False

        # now make episodes
        for new_file in new_files:

            filename, ext = os.path.splitext(new_file['filename'])

            ep = Episode()
            ep.podcast = self
            ep.pub_date = datetime.fromtimestamp(new_file['mtime'])
            datestring = ep.pub_date.strftime("%Y-%m-%d")
            ep.title = "{0} - {1}".format(self.title, datestring)
            ep.description = "{0} for {1}".format(self.title,
                                                  datestring)

            ep.guid = "{0}{1}".format(self.slug, time.time())

            if new_file['part']:
                ep.part = new_file['part']

            # copy audio to buffer, make file object
            rel_path = os.path.join(self.slug, "audio", new_file['filename'])
            print(rel_path)

            with open(new_file['path']) as f:
                new_audio = File(f)
                ep.buffer_audio.save(new_file['filename'], new_audio, save=True)

            print(ep)


        self.last_import = datetime.now()

        self.save()

        self.publish()

        return "Podcast Published"


class Episode(models.Model):

    """
    Episode model, defines a single episode of a podcast and methods to
    extract and set data about the episode.

    """
    podcast = models.ForeignKey(Podcast)
    created = models.DateTimeField('created', auto_now_add=True)
    updated = models.DateTimeField('updated', auto_now=True)
    published = models.DateTimeField('date published', null=True)

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    slug = AutoSlugField(populate_from='title', unique=True, default='')

    track_number = models.IntegerField('real episode number', blank=True,
                                       null=True)
    number = models.CharField('notional episode number', max_length=32,
                              blank=True, null=True)

    description = models.TextField('short episode description',
                                   blank=True, null=True)

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
    show_notes = models.TextField('show notes', blank=True, null=True)
    guests = models.TextField('guests', blank=True, null=True)
    credits = models.TextField('art and music credits', blank=True, null=True)

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
    summary = models.TextField(blank=True)
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

        super(Episode, self).save(*args, **kwargs)

    def tag(self):

        """
        If image or audio were added or updated, the new versions will
        be in the buffer at this point. Any manipulations we do on them
        should happen here, before the episode is published and the files
        get moved out to the world.
        """

        if self.buffer_audio:
            tagged = False

            try:
                audio = PodcastAudio(self.buffer_audio.path)

                if self.podcast.tag_audio:
                    tagged = audio.tag_audio(self)

            except:
                # TODO handle this error
                pass

        # no new audio, but is there a new image?
        if self.buffer_image:

            # do we need to tag it, or did we get it already?
            if not tagged:
                try:
                    audio = PodcastAudio(self.audio.path)
                    audio.tag_audio(self)
                except:
                    pass

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
        Set the published date, but only if this episode is newly published
        or updated
        """
        if self.published and self.updated <= self.published:
            pass
        else:
            self.published = datetime.now()

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
                os.rename(audio_source, audio_dest)
            except:
                # TODO handle this error
                pass

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
                    os.rename(image, image_dest + os.path.basename(image))
            except:
                # TODO handle this
                pass

            self.image = self.buffer_image
            self.buffer_image = None
        self.save()

        return True

    def set_data_from_file(self):
        """
        Set the data for this episode based on its standardized filename

        """

        path = self.podcast.tmp_dir + self.filename
        base_name = self.filename.split('.')[0]
        name_parts = base_name.split('_')
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        date_string = name_parts[1] + " " + datetime.strftime(mtime, "%H:%M:%S")
        self.pub_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

        part = None
        try:
            part = name_parts[2]
        except IndexError:
            pass

        self.part = part
        self.length = check_output(["soxi", "-d", path]).split('.')[0]
        self.size = os.path.getsize(path)
        self.guid = self.filename
        self.title = self.podcast.title + " " + name_parts[1]
        self.description = self.podcast.title + " for " + name_parts[1]
        self.save()

    def save_to_tmp(self, uploaded_file):
        path = self.podcast.tmp_dir + "/" + uploaded_file.name
        with open(path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

    def rename_audio(self):

        if not self.buffer_audio:
            return

        old_filename = self.buffer_audio.name
        date_string = datetime.strftime(self.pub_date, "%Y%m%d")

        ext = os.path.splitext(old_filename)[1]

        rel_path = os.path.dirname(old_filename)

        # construct the new filename
        # <podcast_slug>_<year>-<month>-<day>.ext
        # TODO - make the pattern configurable

        new_filename = "{0}_{1}_{2}{3}".format(self.podcast.slug,
                                               self.number,
                                               date_string,
                                               ext)

        old_path = self.buffer_audio.path

        new_path = os.path.join(settings.BUFFER_ROOT, rel_path, new_filename)

        try:
            os.rename(old_path, new_path)
        except IOError as err:
            return '; '.join(err.messages)

        self.buffer_audio.name = os.path.join(rel_path, new_filename)
        self.save()

    def rename_image(self):
        """
        Note: Do this -before- process_images, otherwise image sizes
        will not have the right name
        """

        if not self.buffer_image:
            return

        old_filename = self.buffer_image.name
        date_string = datetime.strftime(self.pub_date, "%Y%m%d")

        ext = os.path.splitext(old_filename)[1]

        rel_path = os.path.dirname(old_filename)

        # construct the new filename
        # <podcast_slug>_<episode number>_<year><month><day>.ext
        # TODO - make the pattern configurable

        new_filename = "{0}_{1}_{2}{3}".format(self.podcast.slug,
                                               self.number,
                                               date_string,
                                               ext)

        old_path = self.buffer_image.path

        new_path = os.path.join(settings.BUFFER_ROOT, rel_path, new_filename)

        try:
            os.rename(old_path, new_path)
        except IOError as err:
            return '; '.join(err.messages)

        self.buffer_image.name = os.path.join(rel_path, new_filename)
        self.save()
