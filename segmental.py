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

files = os.listdir(tmpdir)

for file in files:
  fileparts = file.split('_')

  file_dict[file] = ("extension"
  if segments == True:
    

  if full == '1':
    outfile = storage + '/' + new_name + extension
    file_in.seek(0)
    full_out = open(outfile, 'a')
    full_out.write(file_in.read())
    full_out.close()

