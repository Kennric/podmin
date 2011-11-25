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
    self.files = os.listdir(podcast.up_dir)
    self.podcast = podcast

  def default(self):
    for file in self.files:
      up_path = self.up_dir + '/' + file
      os.rename(up_path, tmp_dir + "/" + file)

  def newKejo(self):
    # get directories from podcast, process new-style kejo files files are named with the prefix
    # 00539 followed by a 2 digit day code Monday - 11, Tuesday - 12, etc, followed by a 2 digit
    # part number, generally 01 - 08
    # rename the file by the podcast short name, file creation date and part number

    success = True
    last_date = 0
    part = 1

    for file in sorted(self.files):

      uppath = self.podcast.up_dir + '/' + file
      ctime = os.path.getmtime(uppath)

      if ctime > self.podcast.last_run:
        c_date = date.fromtimestamp(ctime)
        short_name = self.podcast.shortname
        filename_parts = file.split(".")
        # parse filename
        prefix = filename_parts[0][0:6]
        day_code = int(filename_parts[0][6])
        part = int(filename_parts[0][7:9])
        extension = filename_parts[1].lower()
        # sanity check
        if ((day_code - 1) != c_date.weekday()):
          print "DIE! Day code does not match date!"
          print "day code: " + str(day_code - 1) + ", weekday: " + str(c_date.weekday())
          success = False

        last_date = c_date
        datetime_string = c_date.strftime("%Y-%m-%d")
        part_string = str(part).zfill(2)
        new_name = self.podcast.shortname + '_' +  datetime_string + '_' + part_string + '.' + extension
        shutil.copy2(uppath, self.podcast.tmp_dir + "/" + new_name)

    return success

class Segmental():
    def __init__(self, podcast):
      self.files = os.listdir(podcast.up_dir)
      self.podcast = podcast

    def combine(self):

