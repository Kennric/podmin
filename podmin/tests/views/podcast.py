from django.test import Client, TestCase
from django.core.urlresolvers import reverse

from podmin.models import Podcast


class TestPodcastViews(TestCase):
    def setUp(self):
        pass

    ###
    # test the views for an anonymous (not logged in) user
    ###
    def test_anon_list_podcasts(self):
        pass

    def test_anon_view_single_podcast_info(self):
        pass

    def test_anon_view_single_podcast_episodes(self):
        pass

    def test_anon_edit_podcast_denied(self):
        pass

    def test_anon_new_podcast_denied(self):
        pass

    def test_anon_delete_podcast_denied(self):
        pass

    ###
    # test the views  for logged-in users
    ###
