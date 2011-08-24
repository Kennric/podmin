from django.db import models
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
import feedparser

class Podcast(models.Model):
  name = models.CharField(max_length=255)
  shortname = models.CharField('short name or abbreiation', max_length=16)
  station = models.CharField('broadcasting station name',max_length=16,blank=True)
  description = models.TextField(blank=True,null=True)
  website = models.CharField(max_length=255,blank=True,null=True)
  contact = models.EmailField(max_length=255,blank=True,null=True)
  pub_dir = models.CharField('path to rss file', max_length=255)
  storage_dir = models.CharField('path to storage location', max_length=255)
  tmp_dir = models.CharField('path to temporary processing location',max_length=255)
  up_dir = models.CharField('path to the upload location',max_length=255)
  combine_segments = models.BooleanField()

  def __unicode__(self):
    return self.name

class Episode(models.Model):
  podcast = models.ForeignKey(Podcast)
  filename = models.CharField('final published file name', max_length=255)
  guid = models.IntegerField('published RSS GUID field', unique=True)
  part = models.IntegerField('part number of a multipart cast',blank=True,null=True)
  pub_date = models.DateTimeField('date published')
  size = models.IntegerField('size in bytes')
  length = models.CharField('length in hours,minutes,seconds', max_length=32,blank=True,null=True)
  description = models.TextField('description / show notes', blank=True,null=True)

  def __unicode__(self):
    return self.filename

  def addToRss(self):
    p = self.podcast

    rss_file = p.pub_dir + "/" + p.shortname + ".xml"

    #feedparser.parse("http://hypothetical.net/beaver/beavercast-full.xml")

  def moveToStorage(self):
    pass

  def addTags(self):
    pass

  def cleanAudio(self):
    pass
