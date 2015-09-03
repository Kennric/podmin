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
        self.files = os.listdir(podcast.config.up_dir)
        self.tmp_dir = podcast.config.tmp_dir
        self.up_dir = podcast.config.up_dir

    def check(self):
        # return true if audio files exist in up_dir
        pass

    def fetch(self):
        # copy files to tmp location
        # add files to self.new_files
        # return new files list
        pass

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


