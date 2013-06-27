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
        return success

    def newKejo(self):
        """
        get directories from podcast, process new-style kejo files
        files are named with the prefix 00539 followed by a 2 digit
        day code Monday - 11, Tuesday - 12, etc, followed by a 2 digit
        part number, generally 01 - 08 rename the file by the podcast
        short name, file creation date and part number
        """
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
                    print "day code: %s, weekday:" % (str(day_code - 1),
                                                      str(c_date.weekday()))
                    success = False

                last_date = c_date
                datetime_string = c_date.strftime("%Y-%m-%d")
                part_string = str(part).zfill(2)
                new_name = "%s_%s_%s.%s" % (self.podcast.shortname,
                                            datetime_string,
                                            part_string, extension)
                new_path = self.podcast.tmp_dir + "/" + new_name
                shutil.copy2(uppath, new_path)

        return success

    def oldKejo(self, file_path):

        success = True
        last_date = 0
        part = 1
        old_files = os.listdir(file_path)
        file_list = []
        for file in sorted(old_files):
            uppath = file_path + '/' + file
            short_name = self.podcast.shortname
            filename_parts = file.split("_")
            print file
            if filename_parts[0] == 'changeme':
                parts = filename_parts[1].split(".")
                date = parts[0].split("-")
                # parse filename
                month = date[0].zfill(2)
                day = date[1].zfill(2)
                year = date[2]
                extension = parts[1].lower()
                datetime_string = "%s-%s-%s" % (year, month, day)

                new_name = "%s_%s.%s" % (self.podcast.shortname,
                                         datetime_string, extension)

                new_path = self.podcast.tmp_dir + "/" + new_name
                shutil.copy2(uppath, new_path)

                file_list.append(new_name)

        return file_list

    def cleanupDirs(self, podcast):
        filelist = [os.path.join(podcast.tmp_dir, f)
                    for f in os.listdir(podcast.tmp_dir)]

        for file in filelist:
            os.remove(file)


class Segment():
    """
    contains methods for combining and managing segmented podcasts
    """
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
            if name_parts[0] != 'dummy':
                mtime = os.path.getmtime(file_path)

            try:
                oldpart = part
                part = int(name_parts[2])
                date = name_parts[1]

                if oldpart > part:
                    no_existing_file = False

                    try:
                        open(combined_file_path)
                    except IOError as e:
                        no_existing_file = True

                    if no_existing_file:
                        self.combineEpisodes(segments, combined_file_path, mtime)
                        #check_output(sox_command)

                    combined_files.append(combined_file_path)
                    segments = []

                segments.append(file_path)

                del name_parts[2]
                combined_file_path = "%s%s%s" % (self.podcast.tmp_dir,
                                                 "_".join(name_parts),
                                                 extension)

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

    def getFiles(self):
        file_list = []
        for file in sorted(self.files):
            file_path = self.podcast.tmp_dir + file
            file_list.append(file_path)

        return file_list

    def combineEpisodes(self, segments, combined_filename, mtime):
        sox_command = ["sox"]
        for segment in segments:
            sox_command.append(segment)

        sox_command.append(combined_filename)
        check_output(sox_command)
        os.utime(combined_filename, (-1, mtime))
