from django.db import models
from django.template.loader import get_template, render_to_string
from django.template import Context, Template
from django.http import HttpResponse
import feedparser
import os

class Podcast(models.Model):
  name = models.CharField(max_length=255)
  shortname = models.CharField('short name or abbreiation', max_length=16)
  station = models.CharField('broadcasting station name',max_length=16,blank=True)
  description = models.TextField(blank=True,null=True)
  website = models.CharField(max_length=255,blank=True,null=True)
  subtitle = models.CharField(max_length=255,blank=True,null=True)
  author = models.CharField(max_length=255,blank=True,null=True)
  contact = models.EmailField(max_length=255,blank=True,null=True)
  pub_dir = models.CharField('path to rss file', max_length=255)
  storage_dir = models.CharField('path to storage location', max_length=255)
  tmp_dir = models.CharField('path to temporary processing location',max_length=255)
  up_dir = models.CharField('path to the upload location',max_length=255)
  combine_segments = models.BooleanField()
  updated = models.DateTimeField()

  def __unicode__(self):
    return self.name

  def publish(self):
    # read rss file, get all unpublished episodes
    # add episodes to rss
    # save rss file
    # set episodes "published"
    # update "updated" field
    rssFile = self.pub_dir + "/" + self.shortname + ".xml"
    rssRaw = feedparser.parse(rssFile)
    rssContext = Context(rssRaw)
    rssTmpFile = rssFile + ".tmp"

    entries = rssContext['entries']

    episodes = self.episode_set.filter(published=0)

    for episode in episodes:
      newEntry = {
          'updated': u'Tue, 23 Aug 2011 12:51 PST',
          'updated_parsed': time.struct_time(tm_year=2011, tm_mon=8, tm_mday=23, tm_hour=20, tm_min=51, tm_sec=0, tm_wday=1, tm_yday=235, tm_isdst=0),
          'links': [
            {'length': u'33966180',
            'href': u'http://hypothetical.net/beaver/JoeBeaverShow/KEJO - ADMINISTRATOR 8-23-2011 ALL.mp3',
            'type': u'audio/mpeg',
            'rel': 'enclosure'},
            {'href': u'http://hypothetical.net/beaver/JoeBeaverShow/KEJO - ADMINISTRATOR 8-23-2011 ALL.mp3',
            'type': 'text/html', 'rel': 'alternate'}
          ],
          'title': u'Tue, 23 Aug 2011 - Full Show',
          'summary_detail': {
            'base': u'http://hypothetical.net/kennric/testo.xml',
            'type': 'text/html',
            'value': u'',
            'language': None},
          'summary': u'',
          'title_detail': {
            'base': u'http://hypothetical.net/kennric/testo.xml',
            'type': 'text/plain',
            'value': u'Tue, 23 Aug 2011 - Full Show',
            'language': None},
          'link': u'http://hypothetical.net/beaver/JoeBeaverShow/KEJO - ADMINISTRATOR 8-23-2011 ALL.mp3'}

    rssString = render_to_string('feed.xml',rssContext)

    out = open(rssFile,'w')
    out.write(rssString)

  def importEpisodes(self):
    # read info from file/settings
    # create episode
    # clean audio, add tags, move to storage
    pass

class Episode(models.Model):
  podcast = models.ForeignKey(Podcast)
  filename = models.CharField('final published file name', max_length=255)
  guid = models.IntegerField('published RSS GUID field', unique=True)
  part = models.IntegerField('part number of a multipart cast',blank=True,null=True)
  pub_date = models.DateTimeField('date published')
  size = models.IntegerField('size in bytes')
  length = models.CharField('length in hours,minutes,seconds', max_length=32,blank=True,null=True)
  description = models.TextField('description / show notes', blank=True,null=True)
  published = models.BooleanField()

  def __unicode__(self):
    return self.filename

  def moveToStorage(self):
    pass

  def addTags(self):
    pass

  def cleanAudio(self):
    pass

