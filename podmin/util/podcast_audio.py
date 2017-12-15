# Podcast Audio class
# Methods for extracting information from and tagging audio files

from subprocess import check_output
import mutagen


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

    def tag_audio(self, episode):
        """
        this method sets the tags, if possible, on the audio file
        tag content is pulled from the episode and podcast instances

        These tags can be set to the same unicode string for both
        tag types:

        MP3/MP4     OGG/FLAC                field
        TALB        ALBUM                   podcast title
        TIT2        TITLE                   episode title
        TIT3        DESCRIPTION             episode description
        TPE1        ARTIST                  podcast author
        TCON        GENRE                   'podcast'
        TRCK        TRACKNUMBER             episode number
        COMM        COMMENT                 show notes
        WXXX        WEBSITE                 podcast website
        TCOP        COPYRIGHT               podcast copyright
        USER        LICENSE                 podcast license
        TDRC        YEAR                    pubdate year

        For these tags, VorbisComment takes multiple tag instances
        while id3 takes a list:
        TIPL        PERFORMER               guests
        TMCL        CREDITS                 credits

        The album art is handled differently as well:
        APIC        METADATA_BLOCK_PICTURE  episode / podcast image


        This tag is a boolean, and is only used by iTunes to mark
        a file as a podcast

        PCST                                True (podcast flag)
        """

        # These fields are optional and could be None
        description = episode.description or ""
        author = episode.podcast.author or ""
        track_number = str(episode.track_number) or ""
        show_notes = episode.show_notes or ""
        website = episode.podcast.website or ""
        copyright = episode.podcast.copyright or ""
        license = episode.podcast.license or ""

        # be sure to cast the strings to unicode
        singleton_tags = [
            {'MP3': 'TALB', 'MP4': 'TALB',  'OggVorbis': 'ALBUM',
             'value': episode.podcast.title.decode('utf-8')},
            {'MP3': 'TIT2', 'MP4': 'TIT2',  'OggVorbis': 'TITLE',
             'value': episode.title.decode('utf-8')},
            {'MP3': 'TIT3', 'MP4': 'TIT3',  'OggVorbis': 'DESCRIPTION',
             'value': description.decode('utf-8')},
            {'MP3': 'TPE1', 'MP4': 'TPE1',  'OggVorbis': 'ARTIST',
             'value': author.decode('utf-8')},
            {'MP3': 'TCON', 'MP4': 'TCON',  'OggVorbis': 'GENRE',
             'value': u'podcast'},
            {'MP3': 'TRCK', 'MP4': 'TRCK',  'OggVorbis': 'TRACKNUMBER',
             'value': track_number.decode('utf-8')},
            {'MP3': 'TIT3', 'MP4': 'TIT3',  'OggVorbis': 'COMMENT',
             'value': show_notes.decode('utf-8')},
            {'MP3': 'WXXX', 'MP4': 'WXXX',  'OggVorbis': 'WEBSITE',
             'value': website.decode('utf-8')},
            {'MP3': 'TCOP', 'MP4': 'TCOP',  'OggVorbis': 'COPYRIGHT',
             'value': copyright.decode('utf-8')},
            {'MP3': 'USER', 'MP4': 'USER',  'OggVorbis': 'LICENSE',
             'value': license.decode('utf-8')},
            {'MP3': 'TDRC', 'MP4': 'TDRC',  'OggVorbis': 'YEAR',
             'value': str(episode.pub_date.year).decode('utf-8')}
        ]

        if episode.guests:
            guests = episode.guests.split('\n')
        else:
            guests = [u'']

        if episode.credits:
            credits = episode.credits.split('\n')
        else:
            credits = [u'']

        """
        we have an image problem. Is this a new audio file that needs
        to be tagged with an existing published image? Is the image new too?
        Where is the image?
        """

        # if the buffer file is set and exists on disk, try that one

        image_data = False

        if episode.buffer_image:
            try:
                image_data = episode.buffer_image.read()
            except Exception:
                image_data = False

        # try the published image istead
        if episode.image and not image_data:
            try:
                image_data = episode.image.read()
            except Exception:
                image_data = False

        # lets try the podcast cover art then
        if episode.podcast.image and not image_data:
            try:
                image_data = episode.podcast.image.read()
            except Exception:
                image_data = False

        if self.filetype in ('MP3', 'MP4'):
            # set singleton tags
            for tag in singleton_tags:
                self.file.tags.add(
                    getattr(mutagen.id3, tag[self.filetype])(
                        encoding=3,
                        text=tag['value'],
                    )
                )

            self.file.tags.add(
                mutagen.id3.TIPL(
                    encoding=3,
                    text=guests,
                )
            )

            self.file.tags.add(
                mutagen.id3.TMCL(
                    encoding=3,
                    text=credits,
                )
            )

            if image_data:
                self.file.tags.add(
                    mutagen.id3.APIC(
                        encoding=3,  # 3 is for utf-8
                        mime=episode.image_type.decode('utf-8'),
                        type=3,  # 3 is for the cover image
                        desc=u'Cover',
                        data=image_data
                    )
                )

        if self.filetype in ('OggVorbis', 'FLAC'):
            print("ogg or flac!")
        """
            for tag in singleton_tags:
                self.file[tag[self.filetype]] = tag['value']

            self.file['PERFORMER'] = guests
            self.file['CREDITS'] = credits


            data = episode.image.read()

            picture = Picture()
            picture.data = data
            picture.type = 17
            picture.desc = u"episode image"
            picture.mime = episode.image_type

            picture_data = picture.write()
            encoded_data = base64.b64encode(picture_data)

            episode_image = encoded_data.decode("ascii")

            self.file["metadata_block_picture"] = [episode_image]
        """

        self.file.save()
        return True
