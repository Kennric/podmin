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


def default(new_files, podcast):

    cleaned_files = []

    new_files.sort()
    part = 0
    old_datetime_string = "1969-01-01"
    for new_file in new_files:

        mtime = os.path.getmtime(new_file)
        mdate = date.fromtimestamp(mtime)

        path, filename = os.path.split(new_file)
        name, extension = os.path.splitext(filename)

        extension = extension.lower()

        datetime_string = mdate.strftime("%Y-%m-%d")

        if datetime_string != old_datetime_string:
            part = 1
            old_datetime_string = datetime_string
        else:
            part += 1

        new_name = "{0}_{1}_{2:0>2}{3}".format(podcast.slug, datetime_string,
                                               part, extension)

        new_path = os.path.join(path, new_name)

        shutil.copy2(new_file, new_path)

        cleaned_files.append(new_path)

    return cleaned_files
