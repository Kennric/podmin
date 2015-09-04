from datetime import datetime, date, time
import re
import time


def new_kejo():
  # get directories from podcast, process new-style kejo files
  # files are named with the prefix 00539 followed by a 2 digit
  # day code Monday - 11, Tuesday - 12, etc, followed by a 2 digit
  # part number, generally 01 - 08
  # rename the file by the podcast short name, file creation date
  # and part number

  print("you have reached new_kejo!")

  """
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
  """
