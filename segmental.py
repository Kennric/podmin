class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value
import rfc822
import os
import ConfigParser
from datetime import datetime, date, time
import re
import time
import mutagen
from operator import itemgetter

# Create an RFC822 compliant date (current time)
today = date.today()
rfc822_date = today
config = ConfigParser.ConfigParser()
config.read('podcast.cfg')

tmpdir = config.get('files', 'tmpdir')
webdir = config.get('files', 'webdir')
storage = config.get('files', 'storage')
podcast_name = config.get('info', 'shortname')
segments = config.get('options','segments') 
full = config.get('options','full')
url = config.get('files','url')

files = os.listdir(tmpdir)
segments = AutoVivification()
#segments = dict()

for file in files:
  file_parts = os.path.splitext(file)
  basename = file_parts[0]
  ext = file_parts[1]

# filename: ktp_2009-03-04_12:03:13.mp3
  fileparts = basename.split('_')
  dt = fileparts[1]
  tm = fileparts[2]
  datetime = time.strptime(dt + "_" + tm, "%Y-%m-%d_%H:%M:%S")
  timestamp = time.mktime(datetime)

  segments[dt][timestamp] = file

dated_segments = iter(sorted(segments.iteritems()))

for day,parts in dated_segments:
  #print k
  #print v
  g = sorted(parts,key=lambda timestamp: (parts[timestamp]))
  i = 1
  for segment in g:
    filename = segments[day][segment]
    file_parts = filename.split("_")
    new_name = file_parts[0] + "_" + file_parts[1] + "_part_" + `i` + "_" + file_parts[2]
    i += 1
