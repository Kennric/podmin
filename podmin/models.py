# django stuff
from django.db import models
from django.contrib.sites.models import Site
#from django.template.loader import get_template
#from django.template import Context
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage
# from django.contrib.sites.models import Site

# django contrib stuff
from autoslug import AutoSlugField

# podmin app stuff
import podmin
from util import podcast_audio, image_sizer

# python stuff
import os
from datetime import datetime, timedelta, date
import requests
import glob

"""
import logging
import re
"""

# audio tagging/processing stuff
import mutagen
from subprocess import check_output
"""
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
"""

buffer_storage = FileSystemStorage(location=settings.BUFFER_ROOT)


def get_image_upload_path(instance, filename):
    if instance.__class__ is Episode:
        return "%s/img/%s" % (instance.podcast.slug, filename)

    if instance.__class__ is Podcast:
        return "%s/img/%s" % (instance.slug, filename)


def get_media_upload_path(instance, filename):
    if instance.__class__ is Episode:
        return "%s/media/%s" % (instance.podcast.slug, filename)

    if instance.__class__ is Podcast:
        return "%s/media/%s" % (instance.slug, filename)


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
    slug = AutoSlugField(populate_from='title', unique=True)
    credits = models.TextField('art and music credits', blank=True, null=True)
    created = models.DateTimeField('created', auto_now_add=True,
                                   editable=False, default=datetime.now())
    updated = models.DateTimeField('updated', auto_now=True)
    website = models.URLField('podcast website', blank=True, null=True)
    frequency = models.CharField(max_length=10,
                                 choices=settings.FREQUENCY_CHOICES,
                                 blank=True, default='never')

    # directories
    buffer_dir = models.CharField('buffer path', max_length=255, blank=True,
                                  default="")
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
    last_import = models.IntegerField(default=1000000000)
    combine_segments = models.BooleanField(default=False)
    publish_segments = models.BooleanField(default=False)
    up_dir = models.CharField('path to the upload location', max_length=255)
    cleaner = models.CharField('file cleaner function name',
                               max_length=255, default='default')
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
    image = models.ImageField('cover art',
                              upload_to=get_image_upload_path)
    copyright = models.CharField(max_length=255, blank=True, null=True)
    license = models.CharField('license',
                               max_length=255, blank=True, null=True,
                               choices=settings.LICENSE_CHOICES)
    copyright_url = models.TextField('copyright url', blank=True, null=True)
    language = models.CharField(max_length=8)
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
                                choices=settings.EXPLICIT_CHOICES, blank=True)
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
        return "%s/img/%s" % (self.storage_url, rss_file)

    @property
    def itunes_image(self):
        file, ext = os.path.splitext(self.image.name)
        return settings.MEDIA_URL + file + "_itunes" + ext

    @property
    def small_image(self):
        file, ext = os.path.splitext(self.image.name)
        return settings.MEDIA_URL + file + "_small" + ext

    @property
    def medium_image(self):
        file, ext = os.path.splitext(self.image.name)
        return settings.MEDIA_URL + file + "_medium" + ext

    @property
    def large_image(self):
        file, ext = os.path.splitext(self.image.name)
        return settings.MEDIA_URL + file + "_large" + ext

    def save(self, *args, **kwargs):

        super(Podcast, self).save(*args, **kwargs)

        """
        Because we use os operations to move files out of the buffer
        and into the publication location, we need to make sure all
        the directories exist. We also want to set these directories
        to some sensible defaults if not specified.
        """
        if self.pub_dir == "":
            print("blank pub_dir!")
            self.pub_dir = "%s/%s" % (settings.MEDIA_ROOT, self.slug)

        if not self.storage_dir:
            self.storage_dir = "%s/%s" % (settings.MEDIA_ROOT, self.slug)

        if not self.buffer_dir:
            self.buffer_dir = "%s/%s" % (settings.BUFFER_ROOT, self.slug)

        if not self.pub_url:
            self.pub_url = "%s%s" % (settings.MEDIA_URL, self.slug)

        if not self.storage_url:
            self.storage_url = "%s%s" % (settings.MEDIA_URL, self.slug)

        if not os.path.isdir(self.pub_dir):
            os.makedirs(self.pub_dir)

        # make sure the media storage directory exists
        media_storage_dir = "%s/media" % self.storage_dir

        if not os.path.isdir(media_storage_dir):
            os.makedirs(media_storage_dir)

        # make sure the image storage directory exists
        img_storage_dir = "%s/img" % (self.storage_dir)

        if not os.path.isdir(img_storage_dir):
            os.makedirs(img_storage_dir)

        # make sure the media buffer directory exists
        media_buffer_dir = "%s/media" % (self.buffer_dir)

        if not os.path.isdir(media_buffer_dir):
            os.makedirs(media_buffer_dir)

        # make sure the image buffer directory exists
        img_buffer_dir = "%s/img" % (self.buffer_dir)

        if not os.path.isdir(img_buffer_dir):
            os.makedirs(img_buffer_dir)

        super(Podcast, self).save(*args, **kwargs)

    def publish(self):
        self.publish_files()
        self.publish_feed()
        self.update_published()
        self.expire_episodes()

        return True

    def publish_files(self):
        """
        Look at the episodes ready for publishing
        if the files exist in the buffer, move them to the published
        location

        """
        expired_date = date.today() - timedelta(days=self.max_age)

        episodes = self.episode_set.filter(pub_date__gte=expired_date,
                                           active=True)

        for episode in episodes:

            audio_file = os.path.basename(episode.audio.name)
            image_file = os.path.basename(episode.image.name)

            audio_source = "%s/media/%s" % (self.buffer_dir, audio_file)
            #image_source = "%s/img/%s" % (self.buffer_dir, image_file)
            image_source = "%s/img/" % (self.buffer_dir)
            image_name, ext = os.path.splitext(image_file)

            audio_destination = "%s/media/%s" % (self.storage_dir, audio_file)
            image_destination = "%s/img/" % (self.storage_dir)


            # if there is audio in the buffer, move it and set data, tag, etc
            if os.path.isfile(audio_source):
                os.rename(audio_source, audio_destination)

            # if there is an image in the buffer, copy it at all its
            # associated resized versions to the storage dir using
            # glob

            if os.path.isfile(image_source + image_file):
                image_glob = image_source + image_name + '*' + ext
                for image in glob.iglob(image_glob):
                    os.rename(image, image_destination + os.path.basename(image))



    def publish_feed(self):
        """
        Pull the feed from the feed generator, store it in the
        pub_dir. For each current episode, move the audio from
        the backlog to storage_dir (Episode.push_audio)

        Feed methods: RssPodcastFeed(), AtomPodcastFeed()
        """

        atom_url = "%s%s%s" % ("http://", Site.objects.get_current().domain,
                               reverse('podcasts_podcast_feed_atom',
                                       args=(self.slug,)))

        atom_feed = requests.request('GET', atom_url).text

        if not self.pub_dir:
            self.pub_dir = "%s/%s" % (settings.MEDIA_ROOT, self.slug)

        atom_file = "%s/atom.xml" % self.pub_dir

        try:
            f = open(atom_file, 'w')
            f.write(atom_feed)
            f.close
        except IOError as err:
            return '; '.join(err.messages)

    def update_published(self):
        """
        Update the 'pubished' date for all the episodes we have just
        published.

        """
        expired_date = date.today() - timedelta(days=self.max_age)
        self.episode_set.filter(pub_date__gte=expired_date,
                                active=True).update(published=datetime.now())

    def expire_episodes(self):
        """
        Expire old episodes by setting active = False where the pubDate
        plus the given delta is less than today's date

        """
        expired_date = date.today() - timedelta(days=self.max_age)

        self.episode_set.filter(pub_date__lte=expired_date,
                                active=True).update(active=False,
                                                    published=None)

    def get_theme(self):
        has_static_dir = os.path.exists(os.path.join(
            settings.PROJECT_ROOT, 'podmin', 'static', 'podcast', self.slug))

        if has_static_dir:
            static_dir = '/static/podcast/%s' % self.slug
        else:
            static_dir = '/static/podcast/default'

        has_template_dir = os.path.exists(os.path.join(
            settings.PROJECT_ROOT, 'podmin', 'templates', 'podmin', 'podcast',
            self.slug))

        if has_template_dir:
            template_dir = self.slug
        else:
            template_dir = 'default'

        return static_dir, template_dir

    def publish_episode(self):
        """
        Manually publish a single episode

        """
        pass

    def auto_publish(self):
        """
        Wrapper method to check for new files on disk and publish
        them if found

        """

        #new_files = self.get_new_files()
        #self.import_from_files(new_files)
        self.expire()
        self.publish()

        return "Podcast Published"

    def get_new_files(self):
        """
        Process new files on disk, calling the podcast's file cleaner
        function, if one is defined.

        """

        file_list = []
        fp = util.FilePrep(self)

        result = getattr(util.FilePrep, self.cleaner)(fp)

        if result:
            # files are moved and renamed
            segmental = util.Segment(self)

            if self.combine_segments:
                combined_episodes = segmental.combine()
                for combined in combined_episodes:
                    file_list.append(combined)

            if self.publish_segments:
                segments = segmental.getSegments()
                for segment in segments:
                    file_list.append(segment)

            if not self.publish_segments and not self.combine_segments:
                full_files = segmental.getFiles()
                for full_file in full_files:
                    file_list.append(full_file)

        return file_list

    def import_from_files(self, file_list):
        """
        Take a list of files and create podcast episodes from them.

        """

        last_date = False

        for file in file_list:
            filename = os.path.basename(file)
            guid = file
            episode = self.episode_set.get_or_create(
                title=self.title,
                filename=filename,
                guid=guid,
                active=True)[0]

            episode.set_data_from_file()
            episode.set_tags()
            # episode.move_to_storage()
            last_date = episode.pub_date

        if last_date:
            self.last_import = int(last_date.strftime("%s"))
            self.save()

    def handle_uploaded_logo(self, form, messages, request):
        uploaded_file = form.cleaned_data['upload_file']

        tmp_path = self.tmp_dir + "/" + uploaded_file.name

        with open(tmp_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # we might want to scale this or something at some point
        # before moving it to its final resting place

        """
        try:
            rescale_image(tmp_path, width, height)
        except Exception, err:
            messages,error(request, "scale failed! " + err)

        """

        # put the logo where it needs to be.
        pub_path = os.path.join(self.pub_dir, 'img', uploaded_file.name)

        try:
            os.rename(tmp_path, pub_path)
        except IOError as err:
            return '; '.join(err.messages)

        self.image = uploaded_file.name


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

    number = models.IntegerField('episode number')

    description = models.TextField('short episode description',
                                   blank=True, null=True)

    audio = models.FileField('audio file', upload_to=get_media_upload_path,
                             storage=buffer_storage)

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
    image = models.ImageField('image', upload_to=get_image_upload_path,
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
        return "%s/media/%s" % (self.podcast.storage_url, audio_filename)

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

    def save(self, *args, **kwargs):

        super(Episode, self).save(*args, **kwargs)

        """
        If image or audio were added or updated, the new versions will
        be in the buffer at this point. Any manipulations we do on them
        should happen here, before the episode is published and the files
        get moved out to the world.
        """

        tagged = False
        # and set some data for convenience
        if os.path.isfile(self.audio.path):

            audio = podcast_audio.PodcastAudio(self.audio.path)

            self.length = audio.duration()

            self.mime_type = audio.get_mimetype()[0]

            if self.podcast.tag_audio:
                tagged = audio.tag_audio(self)

        # resize the episode image
        if os.path.isfile(self.image.path):
            image_sizer.make_image_sizes(self.image.path)
            #while we are here, if we have no new audio but a picture
            #is in the buffer, we should add the image to the already
            #published file
            if not tagged:
                published_audio = os.path.join(self.podcast.storage_dir,
                                               "media",
                                               os.path.basename(self.audio.name))
                audio = podcast_audio.PodcastAudio(published_audio)
                audio.tag_audio(self)

        #if self.podcast.rename_files:
        #    rename_files(self)


    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ["-pub_date, part"]
        get_latest_by = "pub_date"
        order_with_respect_to = 'podcast'
        unique_together = ("podcast", "number")

    def get_absolute_url(self):
        return reverse("episode_show", kwargs={"eid": self.id,
                                               "slug": self.podcast.slug})



    def move_to_storage(self):
        """
        Move an episode to its final web accessible storage location

        """

        # Try to create the storage directory
        try:
            os.makedirs(self.storage_dir)
        except OSError as e:
            raise e

        tmp_path = os.path.join(self.podcast.tmp_dir, self.filename)
        stor_path = os.path.join(self.podcast.storage_dir, self.filename)
        os.rename(tmp_path, stor_path)

    def get_audio_duration(self):
        self.length = check_output(["soxi", "-d", path]).split('.')[0]
        self.save()

    def set_data_from_file(self):
        """
        Set the data for this episode based on its standardized filename

        """

        path = self.podcast.tmp_dir + self.filename
        base_name = self.filename.split('.')[0]
        name_parts = base_name.split('_')
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        date_string = name_parts[
            1] + " " + datetime.strftime(mtime, "%H:%M:%S")
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

    def set_tags(self):
        """
        Set tags to the file, taking the data from the episode variables

        """
        path = self.podcast.tmp_dir + self.filename
        filename, ext = os.path.splitext(path)
        # ext = self.filename.split('.')[1]
        date_string = datetime.strftime(self.pub_date, "%Y-%m-%d")
        tags = dict()
        tags['date'] = date_string
        tags['album'] = self.podcast.title + " " + date_string
        tags['artist'] = self.podcast.author
        tags['length'] = self.length
        tags['copyright'] = datetime.strftime(
            datetime.now(), "%Y") + " " + self.podcast.copyright
        tags['website'] = self.podcast.website

        if self.part:
            tags['tracknumber'] = self.part
            tags['title'] = self.title + " " + \
                date_string + " part " + self.part
        else:
            tags['title'] = self.title + " " + date_string

        tagged = "not yet, ext = " + ext

        if ext == '.mp3':
            tagged = self.tag_mp3(path, tags)

        return tagged

    def tag_mp3(self, file, tags):
        """
        Set mp3 tags to mp3 files

        """
        try:
            audio = mutagen.File(file, easy=True)

            for tag, value in tags.iteritems():
                audio[tag] = value

            audio.save()
        except Exception as err:
            return '; '.join(err.messages)

        #audio.pprint()
        #audio.save()
        return True

    def save_to_tmp(self, uploaded_file):
        path = self.podcast.tmp_dir + "/" + uploaded_file.name
        with open(path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

    def rename_file(self):
        date_string = datetime.strftime(self.pub_date, "%Y-%m-%d")
        extension = os.path.splitext(self.filename)[1]

        new_filename = self.podcast.slug + "_" + date_string + extension
        old_path = self.podcast.tmp_dir + "/" + self.filename
        new_path = self.podcast.tmp_dir + "/" + new_filename

        try:
            os.rename(old_path, new_path)
        except IOError as err:
            return '; '.join(err.messages)

        self.filename = new_filename

        return True

    def handle_uploaded_audio(self, form, messages, request):
        uploaded_file = form.cleaned_data['upload_file']
        upload_filename = uploaded_file.name
        self.filename = upload_filename

        self.save_to_tmp(uploaded_file)

        path = self.podcast.tmp_dir + '/' + self.filename
        self.length = check_output(["soxi", "-d", path]).split('.')[0]
        self.size = uploaded_file.size

        if form.cleaned_data['rename_file']:
            renamed = self.rename_file()
            if renamed is not True:
                messages.error(request,
                               "Problem renaming file: " + renamed)
            else:
                messages.success(request,
                                 "File renamed to " + self.filename)

        if form.cleaned_data['tag_audio']:
            tagged = self.set_tags()
            if tagged is not True:
                messages.warning(request,
                                 "Problem tagging audio: " + tagged)
            else:
                messages.success(request, "Audio tagged successfully")
