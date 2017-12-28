from django.test import Client, TestCase
from django.core.urlresolvers import reverse

from podmin.models import Episode


class TestEpisodeViews(TestCase):
    def setUp(self):
        pass

    ###
    # test the views for an anonymous (not logged in) user
    ###
    def test_anon_view_single_episode_info(self):
        pass

    def test_anon_edit_episode_denied(self):
        pass

    def test_anon_new_episode_denied(self):
        pass

    def test_anon_delete_episode_denied(self):
        pass

    def test_anon_depublish_episode_denied(self):
        pass

    def test_anon_publish_episode_denied(self):
        pass

    def test_anon_mothball_episode_denied(self):
        pass

    ###
    # test the views  for logged-in users
    ###
