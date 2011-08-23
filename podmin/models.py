from django.db import models

class Podcast(models.Model):
  name = models.CharField(max_length=255)
  shortname = models.CharField('short name or abbreiation', max_length=16)
  station = models.CharField('broadcasting station name',max_length=16)
  description = models.CharField(max_length=512)
  website = models.CharField(max_length=255)
  contact = models.CharField(max_length=255)
  pub_dir = models.CharField('path to rss file', max_length=255)
  storage_dir = models.CharField('path to storage location', max_length=255)
  tmp_dir = models.CharField('path to temporary processing location',max_length=255)
  up_dir = models.CharField('path to the upload location',max_length=255)

class Episode(models.Model):
  podcast_id = models.ForeignKey(Podcast)
  filename = models.CharField('final published file name', max_length=255)
  guid = models.IntegerField('published RSS GUID field')
  part = models.IntegerField('part number of a multipart cast')
  pub_date = models.DateTimeField('date published')
  size = models.IntegerField('size in bytes')
  length = models.CharField('length in hours,minutes,seconds', max_length=32)
  description = models.CharField('description / show notes', max_length=1024)

