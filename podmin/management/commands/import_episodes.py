from django.core.management.base import BaseCommand, CommandError
from podmin.models import Episode, Podcast

class Command(BaseCommand):
    help = 'Imports Episodes from files and publishes their Podcast feed.'


    def add_arguments(self, parser):
        parser.add_argument('slug', type=str)


    def handle(self, *args, **options):
        try:
            podcast = Podcast.objects.get(slug=options['slug'])
        except Podcast.DoesNotExist:
            raise CommandError('Podcast "%s" does not exist' % slug)

        podcast.publish_from_files()