# python stuff
from itertools import chain
from mock import patch, call
import shutil
import os

# django stuff
from django.test import TestCase
from django.db import models
from django_markdown.models import MarkdownField
from django.apps import apps
from django.core.files import File
from autoslug import AutoSlugField

# podmin stuff
from podmin.models import Podcast, Episode

###
# Test the Episode model
###


class EpisodeTests(TestCase):

    def setUp(self):
        # make a directory to store any file stuff we test
        if not os.path.isdir('/tmp/podmin_test'):
            os.mkdir('/tmp/podmin_test')

        self.maxDiff = None

        self.expected_fields = {
            '_order': models.fields.proxy.OrderWrt,
            u'id': models.AutoField,
            'created': models.DateTimeField,
            'updated': models.DateTimeField,
            'published': models.DateTimeField,
            'mothballed': models.DateTimeField,
            'title': models.CharField,
            'subtitle': models.CharField,
            'slug': AutoSlugField,
            'track_number': models.IntegerField,
            'number': models.CharField,
            'description': MarkdownField,
            'buffer_audio': models.FileField,
            'audio': models.FileField,
            'guid': models.CharField,
            'part': models.IntegerField,
            'pub_date': models.DateTimeField,
            'size': models.IntegerField,
            'length': models.CharField,
            'mime_type': models.CharField,
            'active': models.BooleanField,
            'tags': models.CharField,
            'show_notes': MarkdownField,
            'guests': MarkdownField,
            'credits': MarkdownField,
            'image': models.ImageField,
            'buffer_image': models.ImageField,
            'image_type': models.CharField,
            'categorization_domain': models.URLField,
            'summary': MarkdownField,
            'priority': models.DecimalField,
            'block': models.BooleanField,
        }

        self.optional_fields = [
            'subtitle',
            'track_number',
            'number',
            'description',
            'part',
            'pub_date',
            'size',
            'length',
            'tags',
            'show_notes',
            'guests',
            'credits',
            'categorization_domain',
            'summary',
            'priority'
        ]

        self.field_defaults = {
            'mime_type': 'application/octet-stream',
            'active': 1,
            'block': False
        }

        self.maximal_episode = {}

        # make a podcast to contain our test episodes
        self.podcast = Podcast.objects.create(
            title='A Test Podcast',
            slug='testo',
            language='en',
            credits='tests by Kennric, music by Jethro Tull',
            published=None,
            website='http://podcast.website.com',
            frequency='weekly',
            pub_url='http://podcast.website.com/rss',
            pub_dir='/tmp/podmin_test/testo/rss',
            storage_dir='/tmp/podmin_test/testo',
            storage_url='http://podcast.website.com/files',
            station='WKRP in Cincinnati',
            description='A test podcast with episodes',
            subtitle='Maximum episode testing.',
            author='Angela Testo',
            contact='angela@example.com',
            copyright='1978 WKRP Inc.',
            license='Public domain',
            copyright_url='http://example.com/license',
            feedburner_url='http://feeds.feedburner.com/not_real',
            tags='test,episodes,etc',
            editor_name='Fred Testo',
            editor_email='fred@example.com',
            webmaster_name='Mary Testo',
            webmaster_email='mary@example.com',
            categorization_domain='http://example.com/taxonomy',
            summary='To summarize, this is a test podcast.',
            explicit='Clean',
            redirect='http://new.website.com/new_location',
            keywords='testing,episodes,WKRP',
            file_rename_format="{podcast}_{date}")

    def tearDown(self):
        # remove any temp files we made in /tmp/podmin_test
        if os.path.isdir('/tmp/podmin_test'):
            shutil.rmtree('/tmp/podmin_test')

    ###
    # Begin the tests
    ###

    def test_fields_defined(self):
        model = apps.get_model('podmin', 'episode')
        for field, field_type in self.expected_fields.items():
            self.assertEqual(
                field_type, type(model._meta.get_field(field)))

    def test_no_extra_fields(self):
        # the following is equivalent to MyField._meta.get_all_field_names()
        # which was deprecated in Django 1.9
        fields = list(set(chain.from_iterable(
            (field.name, field.attname) if hasattr(field, 'attname') else
            (field.name,) for field in Episode._meta.get_fields()
            if not (field.many_to_one and field.related_model is Podcast)
        )))
        
        self.assertEqual(sorted(fields), sorted(self.expected_fields.keys()))

    def test_blank_fields(self):
        apps.get_model('podmin', 'episode')
        for field in self.optional_fields:
            self.assertEqual(Episode._meta.get_field(field).blank, True)

    ###
    # Test the save method
    ###

    def test_creation_with_only_required_fields(self):
        pass

    def test_creation_with_all_fields(self):
        pass

    def test_simple_field_defaults(self):
        pass

    ###
    # Test the meta things
    ###

    def test_order(self):
        pass

    def test_track_number_unique_to_podcast(self):
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
