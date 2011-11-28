import os
import shutil
from datetime import datetime, date, time
import time
import util
from subprocess import check_output

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

      if ctime > self.podcast.last_import:
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
        new_path = self.podcast.tmp_dir + "/" + new_name
        shutil.copy2(uppath, new_path)

    return success

"""
contains methods for combining and managing segmented podcasts
"""
class Segment():
  def __init__(self, podcast):
    self.files = os.listdir(podcast.tmp_dir)
    self.podcast = podcast

  def combine(self):
    segments = []
    combined_files = []
    part = 0

    # hackity-hack
    files = sorted(self.files)
    files.append('dummy_1969-01-01_01.mp3')

    for file in files:
      file_path = self.podcast.tmp_dir + file
      filename = os.path.splitext(file)
      name = filename[0]
      extension = filename[1]
      name_parts = name.split('_')

      try:
        oldpart = part
        part = name_parts[2]
        date = name_parts[1]

        if oldpart > part:
          no_existing_file = False

          try:
            open(combined_file_path)
          except IOError as e:
            no_existing_file = True

          if no_existing_file:
            self.combineEpisodes(segments,combined_file_path)
            #check_output(sox_command)

          combined_files.append(combined_file_path)
          segments = []

        segments.append(file_path)

        del name_parts[2]
        combined_file_path = self.podcast.tmp_dir + "_".join(name_parts) + extension

      except IndexError:
        pass

    return combined_files

  def getSegments(self):
    file_list = []
    for file in sorted(self.files):

      file_path = self.podcast.tmp_dir + file
      filename = os.path.splitext(file)
      name = filename[0]
      name_parts = name.split('_')
      try:
        part = name_parts[2]
        file_list.append(file_path)
      except IndexError:
        pass

    return file_list

  def combineEpisodes(self, segments, combined_filename):
    sox_command = ["sox"]
    for segment in segments:
      sox_command.append(segment)

    sox_command.append(combined_filename)
    check_output(sox_command)



