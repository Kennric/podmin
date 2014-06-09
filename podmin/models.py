# django stuff
from django.db import models
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User
from django.conf import settings
# from django.contrib.sites.models import Site

# django contrib stuff
from autoslug import AutoSlugField

# podmin app stuff
import podmin
import util

# python stuff
import shutil
import os
from datetime import datetime, timedelta, date
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


def get_image_upload_folder(instance, filename):
    # A standardized pathname for uploaded show images
    if instance.__class__ is Episode:
        return "{0}/{1}/img/{2}".format(
            instance.podcast.slug,
            instance.slug, filename)

    if instance.__class__ is Podcast:
        return "{0}/img/{1}".format(instance.slug, filename)


def get_media_upload_folder(instance, pathname):
    # A standardized pathname for uploaded show images
    return "{0}/media".format(instance.podcast.slug)


class Podcast(models.Model):

    """
    Podcast model defines a podcast stream and methods to publish the RSS file

    """
    LICENSE_CHOICES = (
        ('All rights reserved', 'All rights reserved'),
        ('Creative Commons: Attribution (by)',
         'Creative Commons: Attribution (by)'),
        ('Creative Commons: Attribution-Share Alike (by-sa)',
         'Creative Commons: Attribution-Share Alike (by-sa)'),
        ('Creative Commons: Attribution-No Derivatives (by-nd)',
         'Creative Commons: Attribution-No Derivatives (by-nd)'),
        ('Creative Commons: Attribution-Non-Commercial (by-nc)',
         'Creative Commons: Attribution-Non-Commercial (by-nc)'),
        ('Creative Commons: Attribution-Non-Commercial-Share Alike \
            (by-nc-sa)',
         'Creative Commons: Attribution-Non-Commercial-Share Alike \
            (by-nc-sa)'),
        ('Creative Commons: Attribution-Non-Commercial-No Dreivatives \
            (by-nc-nd)',
         'Creative Commons: Attribution-Non-Commercial-No Dreivatives \
            (by-nc-nd)'),
        ('Public domain', 'Public domain'),
        ('Other', 'Other')
    )

    EXPLICIT_CHOICES = (
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Clean', 'Clean'),
    )

    FREQUENCY_CHOICES = (
        ('always', 'Always'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('never', 'Never'),
    )

    # std
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, default=1)
    slug = AutoSlugField(populate_from='title', unique=True)
    last_import = models.IntegerField(default=1000000000)
    combine_segments = models.BooleanField()
    publish_segments = models.BooleanField()
    pub_url = models.URLField('base publication url')
    pub_dir = models.CharField('rss publication path', max_length=255)
    storage_dir = models.CharField('path to storage location', max_length=255)
    storage_url = models.URLField('storage base url')
    tmp_dir = models.CharField('path to temporary processing location',
                               max_length=255)
    up_dir = models.CharField('path to the upload location', max_length=255)
    cleaner = models.CharField('file cleaner function name',
                               max_length=255, default='default')
    credits = models.TextField('art and music credits', blank=True, null=True)
    created = models.DateTimeField('created', auto_now_add=True,
                                   editable=False, default=datetime.now())
    updated = models.DateTimeField('updated', auto_now=True, editable=False,
                                   default=datetime.now())
    website = models.URLField('podcast website', blank=True, null=True)
    rename_files = models.BooleanField()
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES,
                                 blank=True, default='never')

    # RSS specific
    organization = models.CharField(max_length=255, default='')
    station = models.CharField('broadcasting station name',
                               max_length=16, blank=True)
    description = models.TextField(blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    contact = models.EmailField(max_length=255, blank=True, null=True)
    updated = models.DateTimeField(auto_now_add=True)
    image = models.ImageField('cover art', upload_to=get_image_upload_folder)
    copyright = models.CharField('license',
                                 max_length=255, blank=True, null=True,
                                 choices=LICENSE_CHOICES)
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
    explicit = models.BooleanField()
    itunes_categories = models.CharField('itunes cats', max_length=255,
                                         blank=True, null=True)
    categorization_domain = models.URLField(blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    explicit = models.CharField(max_length=255, default='No',
                                choices=EXPLICIT_CHOICES, blank=True)
    block = models.BooleanField(default=False)
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

    # This constant defines the groups and permissions that will be created
    # for each podcast when it is created
    GROUP_PERMS = {'managers': 'manage', 'editors': 'edit',
                   'webmasters': 'web', 'all': 'view'}

    def __unicode__(self):
        return self.title

    @property
    def generator(self):
        return podmin.get_name() + " " + podmin.get_version()

    def publish_episodes(self, episodes, rssFile, type):
        """
        Publish full episodes of the podcast.

        """

        rssBakFile = rssFile + ".bak"
        template = get_template('feed.xml')

        rssContext = Context(self.make_channel(type))
        rssContext['entries'] = []

        for episode in episodes:
            # create a new entry
            entry = episode.build_entry()
            # insert the entry into the rssContext
            rssContext['entries'].insert(0, entry)

            # if the file is in the tmp dir, either it hasn't been put
            # in storage yet (new), or a new version has been uploaded
            # and should overwrite the file in storage

            if os.path.isfile(self.tmp_dir + episode.filename):

                try:
                    episode.move_to_storage()
                except IOError as err:
                    return '; '.join(err.messages)

            else:
                # make sure the file is in storage
                if not os.path.isfile(self.storage_dir + episode.filename):
                    return """Episode {0} from {1} is missing its file:\n
                                 {2} is not found in {3} or {4}
                            """.format(episode.id,
                                       episode.pub_date,
                                       episode.filename,
                                       self.tmp_dir,
                                       self.storage_dir)

        rssContext['feed']['updated'] = datetime.strftime(
            datetime.now(), "%a, %d %b %Y %X") + " PST"

        # copy the existing rss file to a backup, if it exists
        try:
            with open(rssFile):
                shutil.copy2(rssFile, rssBakFile)
        except IOError:
            pass

        # write the new rss file
        try:
            f = open(rssFile, 'w')
            f.write(template.render(rssContext))
            f.close
        except IOError as err:
            return '; '.join(err.messages)

        # now that the rss is written, update the published date
        # on all the episodes we published
        for episode in episodes:
            if not episode.published:
                episode.published = datetime.now()
                episode.save(update_fields=['published'])

        self.updated = datetime.now()
        self.save()

        return True

    def publish(self):
        """
        Wrapper method to publish all new episodes.

        """

        # fp = util.FilePrep(self)
        rssFile = self.pub_dir + self.slug + ".xml"
        episodes = self.episode_set.filter(active=True, part=None,
                                           pub_date__lt=datetime.now())
        type = 'full'
        published = self.publish_episodes(episodes, rssFile, type)

        if self.publish_segments:
            rssFile = self.pub_dir + self.slug + "_segments.xml"
            episodes = self.episode_set.filter(active=1).exclude(part=None)
            type = 'segments'
            published = self.publish_episodes(episodes, rssFile, type)

        # now expire the old episodes
        self.expire()
        # and cleanup directories
        # fp.cleanupDirs(self)
        return published

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

        new_files = self.get_new_files()
        self.import_from_files(new_files)
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

    def expire(self):
        """
        Expire old episodes by setting current = False where the pubDate
        plus the given delta is less than today's date

        """

        delta = timedelta(days=self.max_age)
        expired_date = date.today() - delta
        episodes = self.episode_set.filter(pub_date__lte=expired_date)
        for episode in episodes:
            episode.active = False
            episode.save()

    def make_channel(self, type):
        """
        Update the channel properties of the podcast's RSS file.

        """

        channel = {}
        channel['feed'] = {}
        itunes_cats = []
        if self.itunes_categories:
            cats = self.itunes_categories.split('/')
            for cat in cats:
                pieces = cat.split(':')
                category = pieces[0]
                if len(pieces) > 1:
                    terms = pieces[1].split(',')
                    itunes_cats.append({'name': category, 'terms': [
                                       (x) for x in terms]})
                else:
                    itunes_cats.append({'name': category})
        regular_cats = [(x) for x in self.tags.split(',')]

        if type == 'segments':
            self.subtitle = self.subtitle + " - Segments"

        channel['feed']['title'] = self.title
        channel['feed']['subtitle'] = self.subtitle
        channel['feed']['description'] = self.description
        channel['feed']['links'] = [{'rel': 'alternate',
                                     'type': 'text/html',
                                     'href': self.website,
                                     'title': self.title},
                                    ]

        channel['feed']['rights'] = datetime.strftime(
            datetime.now(), "%Y") + " " + self.copyright

        channel['feed'][
            'generator'] = self.generator
        channel['feed']['language'] = self.language
        channel['feed']['tags'] = regular_cats

        if self.image:
            channel['feed']['image'] = {'href': self.image,
                                        'title': self.title,
                                        'link': self.website}

        if self.ttl:
            channel['feed']['ttl'] = self.ttl

        channel['feed']['author'] = self.author
        channel['feed']['itunes_cats'] = itunes_cats
        channel['feed']['author_detail'] = {
            'email': self.contact, 'name': self.author}
        channel['feed']['itunes_explicit'] = "yes" if self.explicit else "no"
        channel['feed']['itunes_block'] = "no"

        return channel

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

    def handle_uploaded_logo(self, form, messages, request):
        uploaded_file = form.cleaned_data['upload_file']

        tmp_path = self.tmp_dir + "/" + uploaded_file.name

        with open(tmp_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # we might want to scale this or something at some point
        # before moving it to it's final resting place

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
    created = models.DateTimeField('created', auto_now_add=True,
                                   editable=False, default=datetime.now())
    updated = models.DateTimeField('updated', auto_now=True, editable=False,
                                   default=datetime.now())
    published = models.DateTimeField('date published', null=True)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    slug = AutoSlugField(populate_from='title', unique=True, default='')
    description = models.TextField('short episode description',
                                   blank=True, null=True)
    enclosure_file = models.FileField('enclosure file',
                                      upload_to=get_media_upload_folder)
    guid = models.CharField('published RSS GUID field',
                            unique=True, max_length=255)
    part = models.IntegerField(
        'part number of a multipart cast', blank=True, null=True)
    pub_date = models.DateTimeField('rss pubdate', blank=True, null=True)
    size = models.IntegerField('size in bytes', blank=True, null=True)
    length = models.CharField(
        'length in h,m,s format', max_length=32, blank=True, null=True)
    active = models.BooleanField('active', default=1)
    tags = models.CharField(
        'comma separated list of tags', max_length=255, blank=True, null=True)
    show_notes = models.TextField('show notes', blank=True, null=True)

    """
    image: For best results choose an attractive, original, and square JPEG
    (.jpg) or PNG (.png) image at a size of 1400x1400 pixels. Image will be
    scaled down to 50x50 pixels at smallest in iTunes. For reference see
    http://www.apple.com/itunes/podcasts/specs.html#metadata
    """
    image = models.ImageField('image', upload_to=get_image_upload_folder)
    itunes_categories = models.CharField(max_length=255, blank=True)
    # A URL that identifies a categorization taxonomy.
    categorization_domain = models.URLField(blank=True)
    summary = models.TextField(blank=True)
    priority = models.DecimalField(max_digits=2, decimal_places=1,
                                   blank=True, null=True)
    block = models.BooleanField(default=False)

    def __unicode__(self):
        return self.filename

    class Meta:
        ordering = ["-pub_date, part"]
        get_latest_by = "pub_date"
        order_with_respect_to = 'podcast'

    def get_absolute_url(self):
        return reverse("episode", kwargs={"slug": self.id})

    def move_to_storage(self):
        """
        Move an episode to its final web accessible storage location

        """

        # Try to create the storage directory
        try:
            os.makedirs(self.storage_dir)
        except OSError as e:
            raise e

        tmp_path = self.podcast.tmp_dir + self.filename
        stor_path = self.podcast.storage_dir + self.filename
        os.rename(tmp_path, stor_path)

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

    def build_entry(self):
        """
        Build the RSS item entry for this episode

        """

        pubDate = datetime.strftime(
            self.pub_date, "%a, %d %b %Y %H:%M:%S") + " PST"

        if self.podcast.explicit:
            explicit = "yes"
        else:
            explicit = "no"

        tags = [(x) for x in self.podcast.tags.split(',')]
        # at a minimum, we need a pubDate, content, title and enclosure
        entry = {'updated': pubDate,
                 'title': self.title,
                 'title_detail': {
                     'base': u'',
                     'type': 'text/plain',
                     'value': self.title,
                     'language': u'en'
                 },
                 'content': {
                     'base': u'',
                     'type': 'text/plain',
                     'value': self.description,
                     'language': u'en'
                 },
                 'link': self.podcast.storage_url + self.filename,
                 'links': [
                     {'length': self.size,
                      'href': self.podcast.storage_url + self.filename,
                      'type': u'audio/mpeg',
                      'rel': u'enclosure'},
                     {'href':  self.podcast.website,
                      'type': u'text/html',
                      'rel': u'alternate'}
                 ],
                 'id': self.guid,
                 'guidislink': 'false',
                 'itunes_duration': self.length,
                 'itunes_explicit': explicit,
                 'summary_detail': {
                     'base': u'',
                     'type': u'text/html',
                     'value': self.description,
                     'language': None
                 },
                 'summary': self.description,
                 }

        # now add any extra data if we have it
        if self.subtitle:
            entry['subtitle'] = self.subtitle

        if self.tags:
            entry['itunes_keywords'] = tags

        return entry

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
