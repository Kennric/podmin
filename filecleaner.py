import os
import ConfigParser
from datetime import datetime, date, time
import re
import time
import mutagen
from mutagen.easyid3 import EasyID3
    
#audio = EasyID3("example.mp3")
#audio["title"] = u"An example"
#audio.save()

from mutagen.easyid3 import EasyID3
print EasyID3.valid_keys.keys()

config = ConfigParser.ConfigParser()
config.read('podcast.cfg')

tmpdir = config.get('files', 'tmpdir')
storage = config.get('files', 'storage')
podcast_name = config.get('info', 'shortname')

# available tags: ['albumartistsort', 'musicbrainz_albumstatus', 'lyricist', 'releasecountry', 'date', 'performer', 'musicbrainz_albumartistid', 'composer', 'encodedby', 'tracknumber', 'musicbrainz_albumid', 'album', 'asin', 'musicbrainz_artistid', 'mood', 'copyright', 'author', 'media', 'length', 'version', 'artistsort', 'titlesort', 'discsubtitle', 'website', 'musicip_fingerprint', 'conductor', 'compilation', 'barcode', 'performer:*', 'composersort', 'musicbrainz_discid', 'musicbrainz_albumtype', 'genre', 'isrc', 'discnumber', 'musicbrainz_trmid', 'replaygain_*_gain', 'musicip_puid', 'artist', 'title', 'bpm', 'musicbrainz_trackid', 'arranger', 'albumsort', 'replaygain_*_peak', 'organization']

files = os.listdir(tmpdir)


old_date = ""
file_dict = {}

for file in files:
  tmpath = tmpdir + '/' + file

  date = re.search('[0-9]{0,2}-[0-9]{0,2}-[0-9]{4}(?!\d)',file).group()
  tm = re.search('[0-9]{0,2}-[0-9]{2}-[0-9]{2}\s[\w]{2}(?!\d)',file).group()

  tm_pieces = tm.split('-')
  hour = int(tm_pieces[0])
  minute = int(tm_pieces[1])

  second_pieces = tm_pieces[2].split()
  second = int(second_pieces[0])
  ampm = second_pieces[1]

  if ampm == 'PM':
    if hour < 12:
      hour += 12

  good_time = time.strptime(date + "-" + `hour` + "-" + `minute` + "-" + `second`, "%m-%d-%Y-%H-%M-%S")

  print int(time.mktime(good_time))
  print time.strftime("%m-%d-%Y-%H-%M-%S",good_time)


  new_name = podcast_name + '_' + date + "_" + `hour` + ":" + `minute` + ":" + `second`
  
  file_in = open(tmpath,"rb")

  size = os.stat(tmpath).st_size
  extension = os.path.splitext(tmpath)[1]

  print size
  print extension


