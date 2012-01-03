from django.db import models
from django.template.loader import get_template, render_to_string
from django.template import Context, Template
from django.http import HttpResponse
import feedparser
import os
from podmin import util
from datetime import datetime
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from subprocess import check_output

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
  itunes_categories = models.CharField('comma separated list of itunes catergories',max_length=255,blank=True,null=True)
  tags = models.CharField('comma separated list of tags',max_length=255,blank=True,null=True)
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

  def __unicode__(self):
    return self.title

  def publishSegments(self):
    if self.publish_segments:
      rssFile = self.pub_dir + self.shortname + "_segments.xml"
      episodes = self.episode_set.filter(published=1).exclude(part=None)
      for episode in episodes:
        # create a new entry
        entry = episode.buildEntry()
        # insert the entry into the rssContext
        rssContext['entries'].insert(0,entry)
      print template.render(rssContext)

  def publish(self):

    # read rss file into a context
    # get all unpublished episodes
    # for each episode, add episode to context
    # render template with context
    # set episodes "published"
    # update "updated" field
    rssFile = self.pub_dir + self.shortname + ".xml"
    rssRaw = feedparser.parse(rssFile)
    rssContext = Context(rssRaw)
    rssTmpFile = rssFile + ".tmp"
    template = get_template('feed.xml')
    segmentsRssFile = None

    episodes = self.episode_set.filter(published=0,part=None)

    for episode in episodes:
      # create a new entry
      entry = episode.buildEntry()
      # insert the entry into the rssContext
      rssContext['entries'].insert(0,entry)

    #print template.render(rssContext)
    f = open(rssTmpFile, 'w')
    f.write(template.render(rssContext))

  def publishAll(self):

    self.publish()

    if self.publish_segments:
      self.publishSegments()


  def importEpisodes(self):

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

      for file in file_list:
        guid = file
        episode = self.episode_set.create(
                      title = self.title,
                      subtitle = self.subtitle,
                      description = self.description,
                      filename = os.path.basename(file),
                      guid = os.path.basename(file))
        episode.setData()
        episode.setTags()
        episode.moveToStorage()

      self.last_import = int(datetime.now().strftime("%s"))
      self.save()


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
  length = models.CharField('length in hours,minutes,seconds', max_length=32,blank=True,null=True)
  published = models.BooleanField()
  tags = models.CharField('comma separated list of tags',max_length=255,blank=True,null=True)

  def __unicode__(self):
    return self.filename

  def moveToStorage(self):
    tmp_path = self.podcast.tmp_dir + self.filename
    stor_path = self.podcast.storage_dir + self.filename
    os.rename(tmp_path, stor_path)

  def setData(self):
    path = self.podcast.tmp_dir + self.filename
    base_name = self.filename.split('.')[0]
    name_parts = base_name.split('_')

    self.pub_date = datetime.strptime(name_parts[1], "%Y-%m-%d")

    part = None
    try:
      part = name_parts[2]
    except IndexError:
      pass

    self.part = part
    self.length = check_output(["soxi","-d",path])
    self.size = os.path.getsize(path)
    self.save()

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

  def tagMp3(self, file, tags):
    audio = mutagen.File(file, easy=True)

    for tag,value in tags.iteritems():
      audio[tag] = value

    audio.pprint()
    audio.save()

  def buildEntry(self):
    pubDate = datetime.strftime(self.pub_date,"%a, %d %b %Y") + " " + datetime.strftime(datetime.now(), "%X %Z")
    entry = {'updated': pubDate,
              'links': [{'length': self.length,
                          'href': self.podcast.storage_url + self.filename,
                          'type': u'audio/mpeg',
                          'rel': u'enclosure'},
                        {'href':  self.podcast.storage_url + self.filename,
                          'type': u'text/html',
                          'rel': u'alternate'}],
              'title': self.title,
              'summary_detail': {'base': u'',
                                  'type': u'text/html',
                                  'value': self.description,
                                  'language': None},
              'summary': self.description,
              'title_detail': {'base': u'',
                                'type': u'text/plain',
                                'value': self.title,
                                'language': u'en'},
              'link': self.podcast.storage_url + self.filename}
    return entry

