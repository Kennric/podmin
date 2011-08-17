import os
import ConfigParser
from datetime import datetime, date, time
import re
import time
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

#audio = EasyID3("example.mp3")
#audio["title"] = u"An example"
#audio.save()


config = ConfigParser.ConfigParser()
config.read('podcast.cfg')

tmpdir = config.get('files', 'tmpdir')
storage = config.get('files', 'storage')
podcast_name = config.get('info', 'name')
podcast_shortname = config.get('info', 'shortname')
podcast_station = config.get('info', 'station')


files = os.listdir(tmpdir)

old_date = ""
file_dict = {}

for file in files:
  tmpath = tmpdir + '/' + file

  date = re.search('[0-9]{0,2}-[0-9]{0,2}-[0-9]{4}(?!\d)',file).group()
  date_pieces = date.split("-")
  year = date_pieces[2]
  month = date_pieces[0]
  day = date_pieces[1]

  tm = re.search('[0-9]{0,2}-[0-9]{2}-[0-9]{2}\s[\w]{2}(?!\d)',file).group()

  tm_pieces = tm.split('-')
  hour = tm_pieces[0]
  minute = tm_pieces[1]

  second_pieces = tm_pieces[2].split()
  second = int(second_pieces[0])
  ampm = second_pieces[1]

  if ampm == 'PM':
    if hour < 12:
      hour += 12

  good_time = time.strptime(date + ":" + hour + ":" + minute + ":" + second, "%m:%d%Y:%H:%M:%S")

  size = os.stat(tmpath).st_size
  extension = os.path.splitext(tmpath)[1]

  new_name = podcast_shortname + '_' + date + "_" + good_time + extension

  print tmpath
  audio = mutagen.File(tmpath, easy=True)
  audio["title"] = podcast_name
  audio["date"] = year + "-" + month + "-" + day
  audio["artist"] = podcast_station
  audio.pprint()
  audio.save()
  # now rename the file

  file_in = open(tmpath,"rb")
  file_out = open(storage + "/" + new_name, "wb")

  file_out.write(file_in.read())

  file_in.close()
  file_out.close()
  test = mutagen.File(storage + "/" + new_name, easy=True)
  print test.pprint()


# available tags: ['albumartistsort', 'musicbrainz_albumstatus', 'lyricist', 'releasecountry', 'date', 'performer', 'musicbrainz_albumartistid', 'composer', 'encodedby', 'tracknumber', 'musicbrainz_albumid', 'album', 'asin', 'musicbrainz_artistid', 'mood', 'copyright', 'author', 'media', 'length', 'version', 'artistsort', 'titlesort', 'discsubtitle', 'website', 'musicip_fingerprint', 'conductor', 'compilation', 'barcode', 'performer:*', 'composersort', 'musicbrainz_discid', 'musicbrainz_albumtype', 'genre', 'isrc', 'discnumber', 'musicbrainz_trmid', 'replaygain_*_gain', 'musicip_puid', 'artist', 'title', 'bpm', 'musicbrainz_trackid', 'arranger', 'albumsort', 'replaygain_*_peak', 'organization']
