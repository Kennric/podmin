from django.core.management.base import BaseCommand, CommandError
from podmin.models import Podcast
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Imports Episodes from files and publishes their Podcast feed.'

    def add_arguments(self, parser):
        parser.add_argument('slug', type=str)

    def handle(self, *args, **options):
        print("trying to import episodes for {0}".format(options['slug']))
        try:
            podcast = Podcast.objects.get(slug=options['slug'])
        except Podcast.DoesNotExist:
            raise CommandError(
                "Podcast {0} does not exist".format(options['slug']))

        podcast.publish_from_files()
