from datetime import date
import os
import shutil

"""
FIle cleaners may do any manipulation on audio files, but must return
a list of files with standardized names (even if there is only one file)

The filename must be in this format:

{podcast_slug}_{uploaded date}_{optional part number}.{extension}

For instance, a podcast with slug 'testo' with a 2-part mp3 episode
uploaded on Sept 5th 2015 will return:

[testo_2015-09-05_01.mp3, testo_2015-09-05_02.mp3]

A single-part episode must omit the part number:

[testo_2015-09-05.mp3]

"""


# Clean up files that are auto-uploaded from the KEJO radio station
def new_kejo(files, podcast):
    # get directories from podcast, process new-style kejo files
    # files are named with the prefix 00539 followed by a 2 digit
    # day code Monday - 11, Tuesday - 12, etc, followed by a 2 digit
    # part number, generally 01 - 08
    # rename the file by the podcast slug, file creation date
    # and part number

    cleaned_files = []
    files = sorted(files, key=lambda k: k['filename'])

    for f in files:
        mdate = date.fromtimestamp(f['mtime'])

        path, filename = os.path.split(f['path'])
        name, extension = os.path.splitext(filename)

        day_code = int(name[5:7])

        part = name[7:9]

        extension = extension.lower()

        # sanity check
        if ((day_code + 1) != mdate.weekday()):
            print("WARNING: Day code does not match today!")

        datetime_string = mdate.strftime("%Y-%m-%d")

        new_name = "{0}_{1}_{2:0>2}{3}".format(podcast.slug, datetime_string,
                                               part, extension)

        new_path = os.path.join(path, new_name)

        shutil.copy2(f['path'], new_path)

        f['filename'] = new_name
        f['path'] = new_path
        f['cleaned'] = True
        f['part'] = part

        cleaned_files.append(f)

    return cleaned_files
