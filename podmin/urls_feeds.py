from django.conf.urls import patterns, url
from podmin.feeds import RssPodcastFeed, AtomPodcastFeed


urlpatterns = patterns(
    "",
    # Episode list feed by show (RSS 2.0 and iTunes)
    url(r"^(?P<podcast_slug>[-\w]+)/rss/$",
        RssPodcastFeed(), name="podcasts_podcast_feed_rss"),
    # Episode list feed by show (Atom)
    url(r"^(?P<podcast_slug>[-\w]+)/atom/$",
        AtomPodcastFeed(), name="podcasts_podcast_feed_atom"),
    # Episode list feed by show (Media RSS)
    # TODO upon request
)
