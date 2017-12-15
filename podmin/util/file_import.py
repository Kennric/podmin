import os
import shutil
from datetime import datetime
from subprocess import check_call
import importlib
import re
import magic


class FileImporter():
    """
    contains methods for importing files as episodes
    """
    def __init__(self, podcast):
        self.new_files = []
        self.podcast = podcast
        self.status = None

    def scan(self):
        # return true if audio files exist in up_dir
        up_files = os.listdir(self.podcast.up_dir)
        tophat = magic.Magic(mime=True)
        if up_files:
            for up_file in up_files:
                up_file_path = os.path.join(self.podcast.up_dir, up_file)
                mtime = os.path.getmtime(up_file_path)
                is_file = os.path.isfile(up_file_path)
                file_type = tophat.from_file(up_file_path)

                file_date = datetime.fromtimestamp(mtime)
                last = self.podcast.last_import

                if last is None or last < file_date:
                    if is_file and file_type.split('/')[0] == 'audio':
                        up_file = {'filename': up_file,
                                   'type': file_type,
                                   'path': up_file_path,
                                   'mtime': mtime,
                                   'scanned': True,
                                   'part': None}
                        self.new_files.append(up_file)

            if self.new_files:
                self.status = 'checked'
                return True
            else:
                print("no new files!")
        return False

    def fetch(self):
        fetched_files = []
        for new_file in self.new_files:
            source = new_file['path']
            destination = os.path.join(self.podcast.tmp_dir,
                                       new_file['filename'])
            shutil.copy2(source, destination)
            new_file['path'] = destination

            fetched_files.append(new_file)
        self.new_files = fetched_files
        self.status = 'fetched'
        return self.new_files

    def clean(self):
        cleaner_mod = importlib.import_module(
          "podmin.util.file_cleaners." + self.podcast.cleaner)

        cleaner_func = getattr(cleaner_mod, self.podcast.cleaner)

        self.new_files = cleaner_func(self.new_files, self.podcast)

        self.status = 'cleaned'
        return(self.new_files)

    def combine(self):

        if self.status != 'cleaned':
            print("files must be cleaned!")
            return False

        # do the files conform to the standard filename?
        pattern = re.compile(r"""
                             (?P<basename>[a-zA-Z0-9\-]*_
                              [0-9]{4}-[0-9]{2}-[0-9]{2})_
                             (?P<part>[0-9]{2})\.(?P<ext>[\w]*)
                             """, re.X)

        new_files = sorted(self.new_files, key=lambda k: k['filename'])
        combined_files = []
        command = ['sox']

        num_files = len(self.new_files) - 1

        for file_num, new_file in enumerate(new_files):

            path, filename = os.path.split(new_file['path'])
            match = pattern.match(filename)

            if not match:
                print("Files are not named correctly!")
                return False

            if file_num == 0:
                basename = match.group('basename')

            if match.group('basename') != basename or file_num == num_files:
                # we have a new batch of segments! combine the last batch
                # and start on the next set
                new_filename = "{0}_all.{1}".format(basename,
                                                    match.group('ext'))

                if match.group('basename') == basename:
                    command.append(new_file['path'])

                command.append(os.path.join(path, new_filename))

                check_call(command)

                basename = match.group('basename')

                combined_file = {'filename': new_filename,
                                 'type': new_file['type'],
                                 'path': os.path.join(path, new_filename),
                                 'mtime': new_files[file_num - 1]['mtime'],
                                 'scanned': new_file['scanned'],
                                 'combined': True,
                                 'part': None}

                combined_files.append(combined_file)

                self.new_files.append(combined_file)
                command = ['sox']
            else:
                command.append(new_file['path'])

        self.status = 'combined'

        return combined_files

    def cleanup(self):

        deleted_files = []
        if self.status is 'fetched':
            for new_file in self.new_files:
                tmp_file = new_file.path
                os.remove(tmp_file)
                deleted_files.append(tmp_file)

        return deleted_files
