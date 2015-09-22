from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.files import File

from podmin.models import Episode, Podcast

import os
import sqlite3

class Command(BaseCommand):
    help = 'Imports joe Beaver Show Episodes from old podcaster.'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        try:
            podcast = Podcast.objects.get(slug='joebeavershow')
        except Podcast.DoesNotExist:
            raise CommandError('Nope!')


        # open old sqlite db
        # for each episode, build dict
        # make episode with dict
        # columns:
        # 0: 'id', 1: 'podcast_id', 2: 'title', 3: 'subtitle', 4: 'description',
        # 5: 'filename', 6: 'guid', 7: 'part', 8: 'pub_date', 9: 'size',
        # 10:'length', 11: 'current', 12: 'tags', 13: '_order'

        conn = sqlite3.connect('podcaster_dev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM podmin_episode")

        number = 481
        for row in c.fetchall():
            print("importing {0}".format(row[5]))

            episode = Episode()
            episode.podcast = podcast
            episode.title = row[2]
            episode.subtitle = row[3]
            episode.description = row[4]
            episode.guid = row[6]
            episode.part = row[7]
            episode.pub_date = row[8]
            episode.created = row[8]
            episode.updated = row[8]
            episode.published = row[8]
            episode.size = row[9]
            episode.length = row[10]
            episode.active = row[11]
            episode.tags = row[12]
            episode.block = False
            episode.mime_type = "audio/mp3"
            episode.number = number
            episode.track_number = number

            relpath = os.path.join(podcast.slug, "audio", row[5])
            fullpath = os.path.join(settings.MEDIA_ROOT, relpath)

            episode.audio = relpath

            episode.save()

            number += 1

        podcast.publish()

        return "Beaver import acheived, {0} episodes added".format(number - 481)