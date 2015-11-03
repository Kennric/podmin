from django.core.management.base import BaseCommand, CommandError
from podmin.models import Podcast
import logging
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Mothball inactive and expired episodes.'

    def add_arguments(self, parser):
        parser.add_argument('slug', type=str, default=None)

    def handle(self, *args, **options):

        podcast = Podcast.objects.get(slug=options['slug'])
        logger.info("Mothballing {0}".format(podcast.slug))

        expired_date = datetime.now() - timedelta(days=podcast.max_age)
        episodes = self.episode_set.filter(pub_date__lte=expired_date,
                                           active=False)
        for episode in episodes:
            try:
                episode.mothball()
            except:
                raise CommandError(
                    "Could not mothball episode {0}".format(episode.slug))

