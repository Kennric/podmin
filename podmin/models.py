from django.db import models
from django.template.loader import get_template, render_to_string
from django.template import Context, Template
from django.http import HttpResponse
import feedparser
import os
import podmin
from podmin import util
from datetime import datetime
import time
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from subprocess import check_output

"""
Podcast model defines a podcast stream and methods to publish the RSS file

"""
class Podcast(models.Model):
  title = models.CharField(max_length=255)
  shortname = models.CharField('short name or abbreviation', max_length=16)
  station = models.CharField('broadcasting station name',max_length=16,blank=True)
  description = models.TextField(blank=True,null=True)
  website = models.CharField(max_length=255,blank=True,null=True)
  subtitle = models.CharField(max_length=255,blank=True,null=True)
  author = models.CharField(max_length=255,blank=True,null=True)
  contact = models.EmailField(max_length=255,blank=True,null=True)
  updated = models.DateTimeField()
  image = models.CharField('URL for podcast image',max_length=255)
  copyright = models.TextField('copyright statement',blank=True,null=True)
  language = models.CharField(max_length=8)
  explicit = models.BooleanField()
  itunes_categories = models.CharField('itunes cats', max_length=255, blank=True, null=True)
  tags = models.CharField('comma separated list of tags', max_length=255, blank=True, null=True)
  last_import = models.IntegerField()
  combine_segments = models.BooleanField()
  publish_segments = models.BooleanField()
  pub_url = models.CharField('base publication url', max_length=255)
  pub_dir = models.CharField('rss publication path', max_length=255)
  storage_dir = models.CharField('path to storage location', max_length=255)
  storage_url = models.CharField('storage location base url', max_length=255)
  tmp_dir = models.CharField('path to temporary processing location',max_length=255)
  up_dir = models.CharField('path to the upload location',max_length=255)
  cleaner = models.CharField('file cleaner function name',max_length=255)
  # all the iTunes categories we have to choose from

  # set some
  def __unicode__(self):
    return self.title

  """
  Publish segments, where segments are multiple parts of the same episode. The
  segments podcast file is separate from the file of full episodes.

  """
  def publishSegments(self, episodes):
    if self.publish_segments:
      rssFile = self.pub_dir + self.shortname + "_segments.xml"

      for episode in episodes:
        # create a new entry
        entry = episode.buildEntry()
        # insert the entry into the rssContext
        rssContext['entries'].insert(0,entry)
      print template.render(rssContext)

  """
  Publish full episodes of the podcast.

  """
  def publishFull(self, episodes):
    rssFile = self.pub_dir + self.shortname + ".xml"
    rssRaw = feedparser.parse(rssFile)
    rssContext = Context(rssRaw)
    rssBakFile = rssFile + ".bak"
    template = get_template('feed.xml')

    for episode in episodes:
      # create a new entry
      entry = episode.buildEntry()
      # insert the entry into the rssContext
      rssContext['entries'].insert(0,entry)
      episode.published = 1
      episode.save

    rssContext['feed']['updated'] = datetime.strftime(datetime.now(),"%a, %d %b %Y %X") + " PST"

    shutil.copy2(rssFile, rssBakFile)
    f = open(rssFile, 'w')
    f.write(template.render(rssContext))
    f.close

    self.updated = datetime.now()
    self.save()

  """
  Update the channel properties of the podcast's RSS file.

  """
  def updateChannel(self):
    rssFile = self.pub_dir + self.shortname + ".xml"
    rssRaw = feedparser.parse(rssFile)
    rssContext = Context(rssRaw)
    rssBakFile = rssFile + ".bak"
    template = get_template('feed.xml')
    itunes_cats = []
    if self.itunes_categories:
      cats = self.itunes_categories.split('/')
      for cat in cats:
        pieces = cat.split(':')
        category = pieces[0]
        if len(pieces) > 1:
          terms = pieces[1].split(',')
          itunes_cats.append({'name': category, 'terms': [(x) for x in terms]})
        else:
          itunes_cats.append({'name': category})
    regular_cats = [(x) for x in self.tags.split(',')]

    rssContext['feed']['title'] = self.title
    rssContext['feed']['subtitle'] = self.subtitle
    rssContext['feed']['description'] = self.description
    rssContext['feed']['links'] = [ {'rel': 'alternate',
                                    'type': 'text/html',
                                    'href': self.website,
                                    'title': self.title}
                                  ]

    rssContext['feed']['rights'] = self.copyright

    rssContext['feed']['generator'] = podmin.get_name() + " " + podmin.get_version()
    rssContext['feed']['language'] = "en"
    rssContext['feed']['tags'] = regular_cats
    #rssContext['feed']['image'] = (href, title, link)
    #rssContext['feed']['docs'] = ""
    #rssContext['feed']['ttl'] = ""
    rssContext['feed']['author'] = "Joe Beaver"
    rssContext['feed']['itunes_cats'] =  itunes_cats
    rssContext['feed']['author_detail'] = {'email': self.contact, 'name': self.author}
    rssContext['feed']['itunes_explicit'] = "no"
    rssContext['feed']['itunes_block'] = "no"

    shutil.copy2(rssFile, rssBakFile)
    f = open(rssFile, 'w')
    f.write(template.render(rssContext))
    f.close

  """
  Wrapper method to publish all new episodes.

  """
  def publishNew(self):

    episodes = self.episode_set.filter(published=0,part=None)
    self.publishFull(episodes)

    if self.publish_segments:
      episodes = self.episode_set.filter(published=1).exclude(part=None)
      self.publishSegments(episodes)

  """
  Manually publish a single episode

  """
  def publishEpisode(self):
    pass

  """
  Process new files on disk, calling the podcast's file cleaner function, if
  one is defined.

  """
  def getNewFiles(self):

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

  """
  Take a list of files and create podcast episodes from them.

  """

  def importFromFiles(self, file_list):
    for file in file_list:
      guid = file
      episode = self.episode_set.create(
                    title = self.title,
                    filename = os.path.basename(file))
      episode.setDataFromFilename()
      episode.setTags()
      episode.moveToStorage()

    self.last_import = int(datetime.now().strftime("%s"))
    self.save()

"""
Episode model, defines a single episode of a podcast and methods to extract
and set data about the episode.

"""
class Episode(models.Model):
  podcast = models.ForeignKey(Podcast)
  title = models.CharField(max_length=255)
  subtitle = models.CharField(max_length=255,blank=True,null=True)
  description = models.TextField('description / show notes', blank=True,null=True)
  filename = models.CharField('final published file name', max_length=255)
  guid = models.CharField('published RSS GUID field', unique=True, max_length=255)
  part = models.IntegerField('part number of a multipart cast',blank=True,null=True)
  pub_date = models.DateTimeField('date published',blank=True,null=True)
  size = models.IntegerField('size in bytes',blank=True,null=True)
  length = models.CharField('length in hours,minutes,seconds', max_length=32, blank=True, null=True)
  published = models.BooleanField()
  tags = models.CharField('comma separated list of tags', max_length=255, blank=True, null=True)

  def __unicode__(self):
    return self.filename

  """
  Move an episode to its final web accessible storage location

  """
  def moveToStorage(self):
    tmp_path = self.podcast.tmp_dir + self.filename
    stor_path = self.podcast.storage_dir + self.filename
    os.rename(tmp_path, stor_path)

  """
  Set the data for this episode based on its standardized filename

  """
  def setDataFromFilename(self):
    path = self.podcast.tmp_dir + self.filename
    base_name = self.filename.split('.')[0]
    name_parts = base_name.split('_')
    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    date_string = name_parts[1] + " " + datetime.strftime(mtime, "%H:%M:%S")
    self.pub_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    #self.pub_date = datetime.strptime(name_parts[1], "%Y-%m-%d")

    part = None
    try:
      part = name_parts[2]
    except IndexError:
      pass

    self.part = part
    self.length = check_output(["soxi","-d",path]).strip()
    self.size = os.path.getsize(path)
    self.guid = self.filename
    self.title = self.podcast.title + " " + name_parts[1]
    self.description = self.podcast.title + " for " + name_parts[1]
    self.save()

  """
  Set tags to the file, taking the data from the episode variables

  """
  def setTags(self):
    path = self.podcast.tmp_dir + self.filename
    ext = self.filename.split('.')[1]
    date_string = datetime.strftime(self.pub_date,"%Y-%m-%d")
    tags = dict()
    tags['date'] = date_string
    tags['album'] = self.podcast.title + " " + date_string
    tags['author'] = self.podcast.station
    tags['length'] = self.length
    tags['copyright'] = date_string + " " + self.podcast.copyright
    tags['website'] = self.podcast.website
    if self.part:
      tags['tracknumber'] = self.part
      tags['title'] = self.title + " " + date_string + " part " + self.part
    else:
      tags['title'] = self.title + " " + date_string

    # tag the file
    if ext == "mp3":
      self.tagMp3(path,tags)

    return True

  """
  Set mp3 tags to mp3 files

  """
  def tagMp3(self, file, tags):
    audio = mutagen.File(file, easy=True)

    for tag,value in tags.iteritems():
      audio[tag] = value

    audio.pprint()
    audio.save()

  """
  Build the RSS item entry for this episode

  """
  def buildEntry(self):
    pubDate = datetime.strftime(self.pub_date,"%a, %d %b %Y %H:%M:%S") + " PST"
    length = self.length.strip()
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
                'language': u'en',
                'id': self.guid
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
              'itunes_duration': length,
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
