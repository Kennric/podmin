from django.db import models
from django.template.loader import get_template, render_to_string
from django.template import Context, Template
from django.http import HttpResponse
import feedparser
import os
from podmin import util

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
  last_run = models.IntegerField()
  combine_segments = models.BooleanField()
  publish_segments = models.BooleanField()
  publish_combined = models.BooleanField()
  pub_url = models.CharField('base publication url', max_length=255)
  pub_dir = models.CharField('rss publication path', max_length=255)
  storage_dir = models.CharField('path to storage location', max_length=255)
  tmp_dir = models.CharField('path to temporary processing location',max_length=255)
  up_dir = models.CharField('path to the upload location',max_length=255)
  cleaner = models.CharField('file cleaner function name',max_length=255)

  def __unicode__(self):
    return self.title

  def publish(self):
    # if publish_segments, go through process with segment-file
    #    select only episode with part number
    # if publish_combined or if segments = combined = null, use regular file
    # if publish_combined, select only episodes with no part number
    # if segments = combined = null, select all episodes

    # read rss file into a context
    # get all unpublished episodes
    # for each episode, add episode to context
    # render template with context
    # set episodes "published"
    # update "updated" field
    #

    rssFile = self.pub_dir + "/" + self.shortname + ".xml"
    rssRaw = feedparser.parse(rssFile)
    rssContext = Context(rssRaw)
    rssTmpFile = rssFile + ".tmp"

    entries = rssContext['entries']

    episodes = self.episode_set.filter(published=0)

    pass

  def importEpisodes(self):
    # move files from up_dir to tmp_dir for processing

    # run filecleaner - just rename files in tmp_dir
    fp = util.FilePrep(self)
    result = getattr(util.FilePrep, self.cleaner)(fp)

    if result:
      # files are renamed

      #if publish_combined, run segmental to combine episodes
      #   create episode for each combined file
      if self.combine_segments:

      # if publish_segments,
      #   create episode for each part
      #
      #if not publis_combined or publised_segments
      #   create episodes for all files

      # each episode:
      #   clean audio, add tags, move to storage

      print "Yay!"

class Episode(models.Model):
  podcast = models.ForeignKey(Podcast)
  title = models.CharField(max_length=255)
  subtitle = models.CharField(max_length=255)
  description = models.TextField('description / show notes', blank=True,null=True)
  filename = models.CharField('final published file name', max_length=255)
  guid = models.IntegerField('published RSS GUID field', unique=True)
  part = models.IntegerField('part number of a multipart cast',blank=True,null=True)
  pub_date = models.DateTimeField('date published')
  size = models.IntegerField('size in bytes')
  length = models.CharField('length in hours,minutes,seconds', max_length=32,blank=True,null=True)
  published = models.BooleanField()
  tags = models.CharField('comma separated list of tags',max_length=255,blank=True,null=True)

  def __unicode__(self):
    return self.filename

  def moveToStorage(self):
    pass

  def addTags(self):
    pass

  def cleanAudio(self):
    pass

