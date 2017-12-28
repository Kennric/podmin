from django.test import TestCase

from podmin.models import Episode

###
# Test the Episode model
###


class EpisodeTests(TestCase):

    def setup(self):
        pass

    def test_fields_defined(self):
        pass

    ###
    # Test the properties
    ###

    def test_audio_url_property(self):
        pass

    def test_audio_filename_property(self):
        pass

    def test_rss_image_property(self):
        pass

    def test_itunes_image_property(self):
        pass

    def test_small_image_property(self):
        pass

    def test_medium_image_property(self):
        pass

    def test_large_image_property(self):
        pass

    def test_feed_url_property(self):
        pass

    def test_unicode(self):
        pass

    ###
    # Test creation
    ###

    def test_creation_with_required_fields(self):
        pass

    def test_creation_with_all_fields(self):
        pass

    def test_simple_field_defaults(self):
        pass

    def test_numbers_are_podcast_unique(self):
        pass

    def test_numbers_increment(self):
        pass

    ###
    # Test ordering
    ###

    def test_episode_order(self):
        pass

    ###
    # Test misc methods
    ###

    def test_get_absolute_url(self):
        pass

    def test_post_process(self):
        pass

    def test_process_images(self):
        pass

    def test_transform_filenam(self):
        pass

    ###
    # Test file tagging
    ###

    def test_tag_new_audio(self):
        pass

    def test_tag_new_image(self):
        pass

    def test_do_not_tag_if_not_new_image_or_audio(test):
        pass

    ###
    # Test publishing episodes
    ###

    def test_quit_if_already_published(self):
        pass

    def test_quit_if_nothing_buffered(self):
        pass

    def test_move_published_audio(self):
        pass

    def test_move_published_images(self):
        pass

    def test_set_published_length(self):
        pass

    def test_set_published_mime_type(self):
        pass

    def test_update_pub_date_on_publish(self):
        pass

    def test_publish_sets_active(self):
        pass

    def test_publish_unsets_buffer_fields(self):
        pass

    def test_publish_sets_published_fields(self):
        pass

    ###
    # Test depublishing episodes
    ###

    def test_move_depublished_audio(self):
        pass

    def test_move_depublished_images(self):
        pass

    def test_unset_published_on_depublish(self):
        pass

    def test_depublish_sets_inactive(self):
        pass

    def test_depublish_sets_buffer_fields(self):
        pass

    def test_depublish_unsets_published_fields(self):
        pass

    ###
    # Test mothball episodes
    ###

    def test_quit_if_active(self):
        pass

    def test_quit_if_published(self):
        pass

    def test_mothball_directory_creation(self):
        pass

    def test_mothball_file_creation(self):
        pass

    def test_mothball_file_contents(self):
        pass

    def test_mothball_image_files(self):
        pass

    def test_mothball_audio_file(self):
        pass
