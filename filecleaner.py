import os
import sys
import ConfigParser
from datetime import datetime, date, time
import re
import time
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

# read the config file - look in a default place if not provided on the
# command line
config = ConfigParser.ConfigParser()
if len(sys.argv) > 1:
  config.read(sys.argv[1])
else:
  config.read('./podcast.cfg')

# Now get all the config things we need from the file:
# we need the podcast name, shortname, tmp and storage directories
tmpdir = config.get('files', 'tmpdir')
storage = config.get('files', 'storage')
podcast_name = config.get('info', 'name')
podcast_shortname = config.get('info', 'shortname')
podcast_station = config.get('info', 'station')

# get a list of files to process from the temp dir
files = os.listdir(tmpdir)

# for each file, extract info from the filename and get a 
# well formatted name, date, time, etc, rename and insert mp3 tags
for file in files:
  tmpath = tmpdir + '/' + file

# get the date
  date = re.search('[0-9]{0,2}-[0-9]{0,2}-[0-9]{4}(?!\d)',file).group()
  date_pieces = date.split("-")
  year = date_pieces[2]
  month = date_pieces[0]
  day = date_pieces[1]

# get the time
  tm = re.search('[0-9]{0,2}-[0-9]{2}-[0-9]{2}\s[\w]{2}(?!\d)',file).group()
  tm_pieces = tm.split('-')
  hour = tm_pieces[0]
  minute = tm_pieces[1]

# we have an AM/PM string attached, use it to get 24-hour time
  second_pieces = tm_pieces[2].split()
  second = second_pieces[0]
  ampm = second_pieces[1]

  if ampm == 'PM':
    if int(hour) < 12:
      hour = int(hour) + 12
      hour = `hour`

# get a nice datetime object from our dates and times
  datetime_object = time.strptime(date + "-" + hour + ":" + minute + ":" + second, "%m-%d-%Y-%H:%M:%S")
  datetime_string = time.strftime("%Y-%m-%d_%H:%M:%S",datetime_object)
  date_string = time.strftime("%Y-%m-%d",datetime_object)
  time_string = time.strftime("%H:%M:%S",datetime_object)

# get some info about the file
  size = os.stat(tmpath).st_size
  extension = os.path.splitext(tmpath)[1]

# make a nice new name 
  new_name = podcast_shortname + '_' +  datetime_string + extension

# write the new tags to the file
  audio = mutagen.File(tmpath, easy=True)
  audio["title"] = podcast_name
  audio["date"] = year + "-" + month + "-" + day
  audio["artist"] = podcast_station
  audio["version"] = time_string + "-" + `size`
  audio.pprint()
  audio.save()

# now rename the file
  os.rename(tmpath, tmpdir + "/" + new_name)
  test = mutagen.File(tmpdir + "/" + new_name, easy=True)
  print test.pprint()


# available tags: ['albumartistsort', 'musicbrainz_albumstatus', 'lyricist', 'releasecountry', 'date', 'performer', 'musicbrainz_albumartistid', 'composer', 'encodedby', 'tracknumber', 'musicbrainz_albumid', 'album', 'asin', 'musicbrainz_artistid', 'mood', 'copyright', 'author', 'media', 'length', 'version', 'artistsort', 'titlesort', 'discsubtitle', 'website', 'musicip_fingerprint', 'conductor', 'compilation', 'barcode', 'performer:*', 'composersort', 'musicbrainz_discid', 'musicbrainz_albumtype', 'genre', 'isrc', 'discnumber', 'musicbrainz_trmid', 'replaygain_*_gain', 'musicip_puid', 'artist', 'title', 'bpm', 'musicbrainz_trackid', 'arranger', 'albumsort', 'replaygain_*_peak', 'organization']
