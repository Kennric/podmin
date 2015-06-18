#from datetime import timedelta
import mutagen
from subprocess import check_output

class PodcastAudio:

    """
    some methods for getting data about the audio file and setting
    tags in a generic way.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.file = mutagen.File(filepath)
        self.filetype = self.file.__class__.__name__
        self.mime = self.file.mime

    def duration(self):
        """
        turns out mutagen is frequently wrong about durations, so we'll
        call out to soxi instead

        td = timedelta(seconds=self.file.info.length)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return (hours, minutes, seconds)
        """
        return check_output(["soxi", "-d", self.filepath]).split('.')[0]

    def get_mimetype(self):
        # what is the appropriate podcast mimetype? Probably
        # the first in this list, the most specific. But maybe
        # we'll need to do more logic here some day
        return self.mime
