from django.core.management.base import BaseCommand, CommandError
from podmin.models import Podcast
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Publish all feeds, addinf new episodes and expiring old ones.'

    def add_arguments(self, parser):
        parser.add_argument('slug', type=str, default=None)

    def handle(self, *args, **options):

        if options['slug']:
            podcast = Podcast.objects.get(slug=options['slug'])
            logger.info("publishing {0}".format(podcast.slug))
            try:
                podcast.publish()
            except:
                raise CommandError(
                    "Could not publish {0}".format(podcast.slug))
        else:
            podcasts = Podcast.objects.all()

            for podcast in podcasts:
                logger.info("publishing {0}".format(podcast.slug))
                try:
                    podcast.publish()
                except:
                    raise CommandError(
                        "Could not publish {0}".format(podcast.slug))
