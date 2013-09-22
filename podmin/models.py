# django stuff
from django.db import models
from django.template.loader import get_template, render_to_string
from django.template import Context, Template
from django.http import HttpResponse
from django.contrib.auth.models import User

# podmin app stuff
import podmin
from podmin import util

# python stuff
import shutil
import os
from datetime import datetime, timedelta, date
import time
import logging

# audio tagging/processing stuff
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from subprocess import check_output


class Podcast(models.Model):
    """
    Podcast model defines a podcast stream and methods to publish the RSS file

    """

    owner = models.ForeignKey(User, default=1)
    title = models.CharField(max_length=255)
    shortname = models.CharField('short name or abbreviation', max_length=16)
    station = models.CharField(
        'broadcasting station name', max_length=16, blank=True)
    description = models.TextField(blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    contact = models.EmailField(max_length=255, blank=True, null=True)
    updated = models.DateTimeField(auto_now_add=True)
    image = models.CharField('URL for podcast image', 
                             max_length=255, blank=True)
    copyright = models.TextField('copyright statement', blank=True, null=True)
    language = models.CharField(max_length=8)
    explicit = models.BooleanField()
    itunes_categories = models.CharField(
        'itunes cats', max_length=255, blank=True, null=True)
    tags = models.CharField(
        'comma separated list of tags', max_length=255, blank=True, null=True)
    last_import = models.IntegerField(default=1000000000)
    combine_segments = models.BooleanField()
    publish_segments = models.BooleanField()
    pub_url = models.CharField('base publication url', max_length=255)
    pub_dir = models.CharField('rss publication path', max_length=255)
    storage_dir = models.CharField('path to storage location', max_length=255)
    storage_url = models.CharField('storage location base url', max_length=255)
    tmp_dir = models.CharField(
        'path to temporary processing location', max_length=255)
    up_dir = models.CharField('path to the upload location', max_length=255)
    cleaner = models.CharField('file cleaner function name',
                               max_length=255, default='default')
    ttl = models.IntegerField('minutes this feed can be cached', default=1440)
    max_age = models.IntegerField('days to keep an episode', default=365)

    def __unicode__(self):
        return self.title

    def publishEpisodes(self, episodes, rssFile, type):
        """
        Publish full episodes of the podcast.

        """

        rssBakFile = rssFile + ".bak"
        template = get_template('feed.xml')

        rssContext = Context(self.makeChannel(type))
        rssContext['entries'] = [] 

        for episode in episodes:
            # create a new entry
            entry = episode.buildEntry()
            # insert the entry into the rssContext
            rssContext['entries'].insert(0, entry)

            # if the file is in the tmp dir, either it hasn't been put
            # in storage yet (new), or a new version has been uploaded
            # and should overwrite the file in storage

            if os.path.isfile(self.tmp_dir + episode.filename): 
                try: 
                    episode.moveToStorage()
                except IOError, err:
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
        except IOError, err:
            return '; '.join(err.messages)

        self.updated = datetime.now()
        self.save()

        return True

    def publish(self):
        """
        Wrapper method to publish all new episodes.

        """

        # fp = util.FilePrep(self)
        rssFile = self.pub_dir + self.shortname + ".xml"
        episodes = self.episode_set.filter(current=1, part=None, 
                                           pub_date__lt=datetime.now())
        type = 'full'
        published = self.publishEpisodes(episodes, rssFile, type)

        if self.publish_segments:
            rssFile = self.pub_dir + self.shortname + "_segments.xml"
            episodes = self.episode_set.filter(current=1).exclude(part=None)
            type = 'segments'
            published = self.publishEpisodes(episodes, rssFile, type)

        # now expire the old episodes
        self.expire()
        # and cleanup directories
        # fp.cleanupDirs(self)
        return published

    def publishEpisode(self):
        """
        Manually publish a single episode

        """
        pass

    def autoPublish(self):
        """
        Wrapper method to check for new files on disk and publish
        them if found

        """

        new_files = self.getNewFiles()
        self.importFromFiles(new_files)
        self.publish()
        return "Podcast Published"

    def getNewFiles(self):
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

    def importFromFiles(self, file_list):
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
                current=True)[0]

            episode.setDataFromFile()
            episode.setTags()
            # episode.moveToStorage()
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
            episode.current = False
            episode.save()

    def makeChannel(self, type):
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
            subtitle = self.subtitle + " - Segments"

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
            'generator'] = podmin.get_name() + " " + podmin.get_version()
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


class Episode(models.Model):
    """
    Episode model, defines a single episode of a podcast and methods to
    extract and set data about the episode.

    """

    podcast = models.ForeignKey(Podcast)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(
        'short episode description', blank=True, null=True)
    filename = models.CharField('final published file name', max_length=255)
    guid = models.CharField(
        'published RSS GUID field', unique=True, max_length=255)
    part = models.IntegerField(
        'part number of a multipart cast', blank=True, null=True)
    pub_date = models.DateTimeField('date published', blank=True, null=True)
    size = models.IntegerField('size in bytes', blank=True, null=True)
    length = models.CharField(
        'length in h,m,s format', max_length=32, blank=True, null=True)
    current = models.BooleanField('Publish',default=True)
    tags = models.CharField(
        'comma separated list of tags', max_length=255, blank=True, null=True)
    show_notes = models.TextField('show notes', blank=True, null=True)

    def __unicode__(self):
        return self.filename

    class Meta:
        ordering = ["-pub_date, part"]
        get_latest_by = "pub_date"
        order_with_respect_to = 'podcast'

    def moveToStorage(self):
        """
        Move an episode to its final web accessible storage location

        """

        tmp_path = self.podcast.tmp_dir + self.filename
        stor_path = self.podcast.storage_dir + self.filename
        os.rename(tmp_path, stor_path)

    def setDataFromFile(self):
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

    def setTags(self):
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
            tagged = self.tagMp3(path, tags)

        return tagged

    def tagMp3(self, file, tags):
        """
        Set mp3 tags to mp3 files

        """
        try:
            audio = mutagen.File(file, easy=True)

            for tag, value in tags.iteritems():
                audio[tag] = value

            audio.save()
        except Exception, err:
            return '; '.join(err.messages)

        #audio.pprint()
        #audio.save()
        return True

    def buildEntry(self):
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

        new_filename = self.podcast.shortname + "_" + date_string + extension
        old_path = self.podcast.tmp_dir + "/" + self.filename
        new_path = self.podcast.tmp_dir + "/" + new_filename

        try:
            os.rename(old_path, new_path)
        except IOError, err:
            return '; '.join(err.messages)

        self.filename = new_filename

        return True
