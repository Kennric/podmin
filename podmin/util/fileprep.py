import os
import shutil
import sys
import ConfigParser
from datetime import datetime, date, time
import re
import time
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

class FilePrep():
  """
  contains methods for renaming and sorting podcast files

  rename with the following format:
    shortName_year-month-day_xx.mp3
  ex:
    JoeBeaverShow_2011-09-06_01.mp3
  """

  def __init__(self, podcast):
    self.files = os.listdir(podcast.config.up_dir)
    self.tmp_dir = podcast.config.tmp_dir
    self.up_dir = podcast.config.up_dir

  def default(self):
    for file in self.files:
      up_path = self.up_dir + '/' + file
      os.rename(up_path, tmp_dir + "/" + file)

  def newKejo(self):
    # get directories from podcast, process new-style kejo files
    # files are named with the prefix 00539 followed by a 2 digit
    # day code Monday - 11, Tuesday - 12, etc, followed by a 2 digit
    # part number, generally 01 - 08
    # rename the file by the podcast short name, file creation date
    # and part number

    last_date = 0
    part = 1

    for file in self.files:
      # each file in directory:
      # get the ctime
      # if ctime is greater than podcast last_run, process this file
      # parse the filename for day code and part number
      # sanity check day code and ctime
      # generate a datestring for file based on ctime
      # if day code is not the same as the previous day code, increment part
      # generate a filename from datestring and podcast shortname, datestring, and part number
      # copy the file into the tmpdir with its new name string
      tmpath = self.up_dir + '/' + file
      ctime = os.path.getctime(tmppath)

      if ctime > podcast.last_run
        c_date = date.fromtimestamp(ctime)
        short_name = podcast.short_name
        filename_parts = file.split(".")
        # parse filename
        prefix = filename_parts[0][0:6]
        day_code = filename_parts[0][6]
        part = filename_parts[0][7:9]
        extension = filename_parts[1].lower
        # sanity check
        if ((day_code + 1) != c_date.weekday)
          print "DIE! Day code does not match date!"
        else

        if c_date == last_date
          part = part + 1
        else
          part = 1

        datetime_string =  c_date.strftime("%Y-%m-%d")
        part = str(part).zfill(2)

        new_name = podcast_shortname + '_' +  datetime_string + '_' + part + '.' + extension
        shutil.copy2(tmpath, tmpdir + "/" + new_name)


