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

import file_cleaners *

class FilePrep():
  """
  contains methods for renaming and sorting podcast files

  rename with the following format:
    shortName_year-month-day_xx.mp3
  ex:
    JoeBeaverShow_2011-09-06_01.mp3
  """

  """
  get the relevant settings from the podcast and a list
  of files to work on, then send these to a cleaner method


  """
  def __init__(self, podcast):
    self.files = os.listdir(podcast.config.up_dir)
    self.tmp_dir = podcast.config.tmp_dir
    self.up_dir = podcast.config.up_dir

  def get_files(self):
    # copy files to tmp location
    # add files to self.new_files

  def clean(self):
    # use defined filecleaner, or default, to prepare
    # files
    # filecleaner should return dict of filenames and
    # associated data 
    # update self.new_files with new filenames

  def combine(self):
    # combine multiple episodes

  def get_episodes(self):
    # return a list of episode arrays (one episode if
    # single file or combined

  def default(self):
    for file in self.files:
      up_path = self.up_dir + '/' + file
      os.rename(up_path, tmp_dir + "/" + file)


