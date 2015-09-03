from podmin.models import Episode

import os
import shutil
from datetime import datetime, date, time
import re

from file_cleaners import *


class FileImporter():
    """
    contains methods for importing files as episodes
    """

    def __init__(self, podcast):
        self.new_files = []
        self.tmp_dir = podcast.config.tmp_dir
        self.up_dir = podcast.config.up_dir

    def check(self):
        # return true if audio files exist in up_dir
        up_files = os.listdir(podcast.config.up_dir)
        if up_files:
            for up_file in up_files:
                filepath = os.path.join(podcast.config.up_dir, up_file)
                # check file type
                self.new_files.append(filepath)
            if self.new_files:
                return True
        return False
         
    def fetch(self):
        new_new_files = []
        for new_file in self.new_files:
            source = os.path.join(podcast.config.up_dir, new_file)
            destination = os.path.join(podcast.config.tmp_dir, new_file)
            os.copy2(source, destination)
            new_new_files.append(destination)
        
        self.new_files = new_new_files
        return self.new_files

    def clean(self):
        # use defined filecleaner, or default, to prepare files
        # update self.new_files with new filenames
        # return new files list
        pass

    def combine(self):
        # combine multiple files
        # update self.new_files
        # return new files list
        pass

    def episodify(self):
        # return a list of episodes, one per self.new_files
        pass

    def default(self):
        for file in self.files:
            up_path = self.up_dir + '/' + file
            os.rename(up_path, tmp_dir + "/" + file)


