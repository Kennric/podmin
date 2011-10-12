import rfc822
import os
import ConfigParser
from datetime import datetime, date, time
import re
import time
import mutagen
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

full_rss_outfile = webdir + "/" +  config.get('info','shortname') + "_full_rss.xml"
segments_rss_outfile = webdir + "/" +  config.get('info','shortname') + "_segments_rss.xml"

##
# Make sure the podcasts have the right permissions
##
perms = 644
files = os.listdir(tmpdir)

##
# Open the rss output file(s)
##
if segments == 1:
  seg_rss = open(segments_rss_outfile,'r')

if full == 1:
  full_rss = open(full_rss_outfile,'r')

##
# Process incoming files:
##
segment = 1
seg_items = ''
full_items = ''
data = ''
fullsize = 0
old_date = ''
old_name = ''

for file in files:
  tmpath = tmpdir + '/' + file
  #os.chmod(tmpath, perms)
  
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
  print date + "-" + `hour` + "-" + `minute` + "-" + `second`
  
  new_name = podcast_name + '_' + date
  if old_name == '': old_name = new_name
  
  if date == old_date: 
    segment += 1 
  else: segment = 1

  old_date = date
  file_in = open(tmpath,"rb")

  size = os.stat(tmpath).st_size 
  extension = os.path.splitext(tmpath)[1]

  if segments == '1':
    outfile = storage + '/' + new_name + "-Part_" + `segment` + extension
    fileout = open(outfile,'wb')
    fileout.write(file_in.read())
    fileout.close 
    seg_items += '\n\t<pubDate>$rfc822_date $hour:$minute PST</pubDate>\n'
    seg_items += '\t<enclosure\n'
    seg_items += '\t\turl=' + url + '/' + file + '\n' 
    seg_items += '\t\tlength=' + `size` + '\n'
    seg_items += '\t\ttype="audio/mpeg"\n'
    seg_items += '\t/>\n'
    seg_items += '\t<link>' + url + '/' + file + '</link>\n'

  if full == '1':
    outfile = storage + '/' + new_name + extension
    file_in.seek(0)
    full_out = open(outfile, 'a')
    full_out.write(file_in.read())
    full_out.close()

