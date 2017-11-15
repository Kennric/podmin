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
import podmin
from util.podcast_audio import PodcastAudio
from util import image_sizer
from util.file_import import FileImporter
from constants import *

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
    credits = MarkdownField('art and music credits', blank=True, null=True)
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
    up_dir = models.CharField('path to the upload location', max_length=255,
                              blank=True, null=True)
    cleaner = models.CharField('file cleaner function name',
                               max_length=255, blank=True, null=True)

    # general file manipulation things
    rename_files = models.BooleanField(default=False)
    tag_audio = models.BooleanField(default=True)

    # RSS specific
    organization = models.CharField(max_length=255, default='')
    station = models.CharField('broadcasting station name',
                               max_length=16, blank=True)
    description = MarkdownField(blank=True, null=True)
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
    max_age = models.IntegerField('days to keep an episode', default=0)
    editor_name = models.CharField(max_length=255, blank=True, null=True)
    editor_email = models.EmailField('editor email', blank=True)
    webmaster_name = models.CharField(max_length=255, blank=True, null=True)
    webmaster_email = models.EmailField('webmaster email', blank=True)

    # itunes specific

    categorization_domain = models.URLField(blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    summary = MarkdownField(blank=True)
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

    file_rename_format = models.CharField(
        'file name pattern',
        max_length=32,
        default="{podcast}_{number:0>2}_{date}")

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

    @property
    def feed_url(self):
        filename = "{0}.xml".format(self.feed_format)
        return "{0}/{1}".format(self.pub_url, filename)

    def save(self, *args, **kwargs):
        """
        set these urls to local media urls if not specified.
        """

        media_url = urlparse(settings.MEDIA_URL)
        if media_url['scheme'] and media_url['netloc']
            file_url = "{0}{1}".format(settings.MEDIA_URL, self.slug)
        else
            file_url = "http://{0}{1}{2}".format(
                Site.objects.get_current().domain,
                settings.MEDIA_URL, self.slug)

        if not self.pub_url:
            self.pub_url = file_url
        if not self.storage_url:
            self.storage_ur = file_url

        image_pub_dir = os.path.join(settings.MEDIA_ROOT, self.slug, "img")
        audio_pub_dir = os.path.join(settings.MEDIA_ROOT, self.slug, "audio")
        image_buffer_dir = os.path.join(settings.BUFFER_ROOT, self.slug, "img")
        audio_buffer_dir = os.path.join(
            settings.BUFFER_ROOT, self.slug, "audio")

        """
        make sure dirs exist
        """
        error_msg = "{0}: Directory creation error: {1}"
        if not os.path.isdir(image_pub_dir):
            try:
                os.makedirs(image_pub_dir)
            except OSError as err:
                logger.error(error_msg.format(self.slug, err))
                pass

        if not os.path.isdir(audio_pub_dir):
            try:
                os.makedirs(audio_pub_dir)
            except OSError as err:
                logger.error(error_msg.format(self.slug, err))
                pass

        if not os.path.isdir(image_buffer_dir):
            try:
                os.makedirs(image_buffer_dir)
            except OSError as err:
                logger.error(error_msg.format(self.slug, err))
                pass

        if not os.path.isdir(audio_buffer_dir):
            try:
                os.makedirs(audio_buffer_dir)
            except OSError as err:
                logger.error(error_msg.format(self.slug, err))
                pass

        super(Podcast, self).save(*args, **kwargs)

    def publish(self):
        self.publish_episodes()
        # if this podcast has a max age, then expire old episodes
        if self.max_age > 0:
            self.expire_episodes()
        self.publish_feed()

        return True

    def publish_episodes(self):
        # if podcast max_age is 0, then episodes never expire.
        if self.max_age > 0:
            # publish episodes that are ripe
            expired_date = datetime.now() - timedelta(days=self.max_age)

            episodes = self.episode_set.filter(pub_date__gte=expired_date,
                                               pub_date__lte=datetime.now(),
                                               active=True)
        else:
            episodes = self.episode_set.filter(pub_date__lte=datetime.now(),
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

        logger.info("{0}: writing feed to {1}".format(self.slug, feed_file))
        try:
            f = open(feed_file, 'w')
            f.write(feed_content)
            f.close
        except IOError as err:
            logger.error("{0}: feed writing error: {1}".format(self.slug, err))

        self.published = datetime.now()

        self.save()

    def expire_episodes(self):
        """
        Expire old episodes where the pubDate < today - max age

        """
        expired_date = datetime.now() - timedelta(days=self.max_age)

        episodes = self.episode_set.filter(pub_date__lte=expired_date)

        for episode in episodes:
            logger.info("{0}: expiring episodes".format(self.slug))
            episode.depublish()

    def publish_from_files(self):
        """
        Wrapper method to check for new files on disk and publish
        them if found
        """

        logger.info("{0}: updating from files".format(self.slug))
        # if the up_dir is not set, what are we even doing here?
        if not self.up_dir:
            logger.error("{0}: failed: up_dir not set".format(self.slug))
            return False

        # if the up_dir isn't a directory, this is going nowhere
        if not os.path.isdir(self.up_dir):
            logger.error("{0}: failed: up_dir not a dir".format(self.slug))
            return False

        try:
            importer = FileImporter(self)
        except:
            logger.error("{0}: importer failed to init".format(self.slug))
            return False

        status = importer.scan()

        if not status:
            logger.info("{0}: no new files".format(self.slug))
            return False

        try:
            new_files = importer.fetch()
        except:
            logger.error(
                "{0}: failed: couldn't fetch new files".format(self.slug))
            return False

        try:
            new_files = importer.clean()
        except:
            logger.error(
                "{0}: failed: couldn't clean new files".format(self.slug))
            return False

        if self.combine_segments:
            try:
                new_files = importer.combine()
            except:
                logger.error(
                    "{0}: failed: couldn't combine segments".format(self.slug))
                return False

        try:
            last = Episode.objects.filter(podcast=self).latest()
            number = last.track_number + 1
        except:
            # maybe this is the first?
            number = 1

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
            ep.number = number
            ep.track_numer = number

            # number += 1

            ep.guid = "{0}{1}".format(self.slug, time.time())

            if new_file['part']:
                ep.part = new_file['part']
            else:
                number += 1

            # copy audio to buffer
            new_filename = ep.transform_filename(new_file['filename'])

            destination = os.path.join(settings.BUFFER_ROOT,
                                       self.slug,
                                       "audio",
                                       new_filename)

            logger.info("{0}: creating new episode".format(self.slug))

            ep.size = os.path.getsize(new_file['path'])

            shutil.copy2(new_file['path'], destination)

            ep.buffer_audio = os.path.join(self.slug, "audio", new_filename)

            ep.save()

            logger.info("{0}: Episode created: \n{1}\n{2}".format(
                self.slug, ep.title, ep.buffer_audio))

            ep.post_process()

        self.last_import = datetime.now()

        self.save()

        self.publish()

        deleted_files = importer.cleanup()

        logger.info("{0}: deleted {1}".format(self.slug,
                                              ', '.join(deleted_files)))

    def transform_filename(self, filename):
        if not self.rename_files:
            return filename

        old, ext = os.path.splitext(filename)

        pattern = re.compile(r"\W", re.X)

        attributes = {'episode': "",
                      'podcast': self.slug,
                      'number': "cover",
                      'track_number': "",
                      'guid': "",
                      'part': "",
                      'tags': pattern.sub("_",  self.tags or ""),
                      'org': pattern.sub("_", self.organization or ""),
                      'author': pattern.sub("_", self.organization or ""),
                      'date': time.strftime("%Y%m%d")
                      }

        new = "{0}{1}".format(
            self.file_rename_format.format(**attributes), ext)

        logger.info("{0}: saving {1} as {2}".format(self.slug, old, new))

        return new

    def make_mothball(self):
        logger.info("{0}: making mothball dirs".format(self.slug))

        mothball_dir = os.path.join(settings.ARCHIVE_ROOT, self.slug)
        mothball_img = os.path.join(settings.ARCHIVE_ROOT, self.slug, 'img')
        mothball_audio = os.path.join(settings.ARCHIVE_ROOT, self.slug,
                                      'audio')
        mothball_episodes = os.path.join(settings.ARCHIVE_ROOT, self.slug,
                                         'episodes')

        if not os.path.isdir(mothball_dir):
            logger.info("{0}: making {1}".format(self.slug, mothball_dir))
            try:
                os.makedirs(mothball_dir)
            except OSError as err:
                logger.error(error_msg.format(self.slug, err))

        if not os.path.isdir(mothball_img):
            logger.info("{0}: making {1}".format(self.slug, mothball_img))
            try:
                os.makedirs(mothball_img)
            except OSError as err:
                logger.error(error_msg.format(self.slug, err))

        if not os.path.isdir(mothball_audio):
            logger.info("{0}: making {1}".format(self.slug, mothball_audio))
            try:
                os.makedirs(mothball_audio)
            except OSError as err:
                logger.error(error_msg.format(self.slug, err))

        if not os.path.isdir(mothball_episodes):
            logger.info("{0}: making {1}".format(self.slug, mothball_episodes))
            try:
                os.makedirs(mothball_episodes)
            except OSError as err:
                logger.error(error_msg.format(self.slug, err))

        # serialize podcast
        podcast_filename = "{0}_{1}.json".format(
            self.slug, datetime.strftime(datetime.now(), "%Y%m%d"))

        podcast_file = os.path.join(mothball_dir, podcast_filename)

        # serialize current data
        podcast = serializers.serialize('json', [self])

        # save serialized data to mothball_dir
        with open(podcast_file, 'w+') as f:
            f.write(podcast)

        # move files from buffer to mothball_dir
        if self.image:
            image_file = os.path.basename(self.image.name)

            image_source = os.path.dirname(self.image.path) + "/"
            image_name, ext = os.path.splitext(image_file)

            image_dest = os.path.join(settings.ARCHIVE_ROOT,
                                      os.path.dirname(self.image.name),
                                      "")
            try:
                image_glob = image_source + image_name + '*' + ext
                for image in glob.iglob(image_glob):
                    shutil.copy2(image, image_dest + os.path.basename(image))
            except:
                logger.error("{0}: mothball failed: {2}".format(
                    self.slug, err))
                return False


class Episode(models.Model):

    """
    Episode model, defines a single episode of a podcast and methods to
    extract and set data about the episode.

    """
    podcast = models.ForeignKey(Podcast)
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
