from django.test import TestCase, override_settings
from django.db import models
from django_markdown.models import MarkdownField
from django.apps import apps

from itertools import chain

from podmin.models import Podcast, Episode


###
# Test the Podcast model
###
class PodcastTests(TestCase):

    def setUp(self):
        self.maxDiff = None

        self.expected_fields = {
            u'id': models.AutoField,
            'title': models.CharField,
            'owner': models.ForeignKey,
            u'owner_id': models.ForeignKey,
            'slug': models.SlugField,
            'credits': MarkdownField,
            'created': models.DateTimeField,
            'published': models.DateTimeField,
            'updated': models.DateTimeField,
            'website': models.URLField,
            'frequency': models.CharField,
            'active': models.BooleanField,
            'feed_format': models.CharField,
            'pub_url': models.URLField,
            'pub_dir': models.CharField,
            'storage_dir': models.CharField,
            'storage_url': models.URLField,
            'tmp_dir': models.CharField,
            'last_import': models.DateTimeField,
            'combine_segments': models.BooleanField,
            'publish_segments': models.BooleanField,
            'up_dir': models.CharField,
            'cleaner': models.CharField,
            'rename_files': models.BooleanField,
            'tag_audio': models.BooleanField,
            'organization': models.CharField,
            'station': models.CharField,
            'description': MarkdownField,
            'subtitle': models.CharField,
            'author': models.CharField,
            'contact': models.EmailField,
            'image': models.ImageField,
            'copyright': models.CharField,
            'license': models.CharField,
            'copyright_url': models.TextField,
            'language': models.CharField,
            'feedburner_url': models.URLField,
            'ttl': models.IntegerField,
            'tags': models.CharField,
            'max_age': models.IntegerField,
            'editor_name': models.CharField,
            'editor_email': models.EmailField,
            'webmaster_name': models.CharField,
            'webmaster_email': models.EmailField,
            'categorization_domain': models.URLField,
            'summary': MarkdownField,
            'explicit': models.CharField,
            'block': models.BooleanField,
            'itunes_categories': models.ManyToManyField,
            'redirect': models.URLField,
            'keywords': models.CharField,
            'itunes_url': models.URLField,
            'file_rename_format': models.CharField,
            'episode': models.ManyToOneRel}

        self.optional_fields = [
            'credits',
            'published',
            'website',
            'frequency',
            'pub_url',
            'pub_dir',
            'storage_dir',
            'storage_url',
            'last_import',
            'up_dir',
            'cleaner',
            'station',
            'description',
            'subtitle',
            'author',
            'contact',
            'copyright',
            'license',
            'copyright_url',
            'feedburner_url',
            'tags',
            'editor_name',
            'editor_email',
            'webmaster_name',
            'webmaster_email',
            'categorization_domain',
            'summary',
            'explicit',
            'itunes_categories',
            'redirect',
            'keywords',
            'itunes_url'
        ]

        self.required_fields = [
            'title',
            'slug',
            'language'
        ]

        self.minimal_podcast = {
            'title': 'A Minimal Podcast',
            'slug': 'minimal',
            'language': 'en'}

        self.maximal_podcast = {
            'title': 'A Maximal Podcast',
            'slug': 'maximal',
            'language': 'en',
            'credits': 'tests by Kennric',
            'published': None,
            'website': 'http://a.website.com',
            'frequency': 'weekly',
            'pub_url': 'http://a.website.com/rss',
            'pub_dir': '/tmp/podmin/maximal/rss',
            'storage_dir': '/tmp/podmin/maximal',
            'storage_url': 'http://a.website.com/files',
            'last_import': None,
            'up_dir': '/tmp/upload',
            'cleaner': 'testcleaner',
            'station': 'WKRP in Cincinnati',
            'description': 'A test podcast with all the fields',
            'subtitle': 'Maximum fieldage for testing.',
            'author': 'Angela Testo',
            'contact': 'angela@example.com',
            'copyright': '1978 WKRP Inc.',
            'license': 'Public domain',
            'copyright_url': 'http://example.com/license',
            'feedburner_url': 'http://feeds.feedburner.com/not_real',
            'tags': 'test,maximal,etc',
            'editor_name': 'Fred Testo',
            'editor_email': 'fred@example.com',
            'webmaster_name': 'Mary Testo',
            'webmaster_email': 'mary@example.com',
            'categorization_domain': 'http://example.com/taxonomy',
            'summary': 'To summarize, this is a test podcast.',
            'explicit': 'Clean',
            'redirect': 'http://b.website.com/new_location',
            'keywords': 'testing,maximal,WKRP',
            'itunes_url': 'http://itunes.example.com/maximal',
            'file_rename_format': "{podcast}_{date}"
            }

        # These fields have explicit, static (not derived) default values
        # Test derived defaults (urls and directories, for example)
        # separately.
        self.field_defaults = {
            'frequency': 'never',
            'feed_format': 'rss',
            'tmp_dir': '/tmp',
            'rename_files': False,
            'tag_audio': True,
            'organization': '',
            'ttl': 1440,
            'max_age': 0,
            'explicit': 'No',
            'block': False,
            'file_rename_format': "{podcast}_{number:0>2}_{date}",
            'image': './static/img/default_podcast.png'
        }

    def test_fields_defined(self):
        model = apps.get_model('podmin', 'podcast')
        for field, field_type in self.expected_fields.items():
            self.assertEqual(
                field_type, type(model._meta.get_field(field)))

    def test_no_extra_fields(self):
        # the following is equivalent to MyField._meta.get_all_field_names()
        # which was deprecated in Django 1.9
        fields = list(set(chain.from_iterable(
            (field.name, field.attname) if hasattr(field, 'attname') else
            (field.name,) for field in Podcast._meta.get_fields()
            if not (field.many_to_one and field.related_model is Episode)
        )))
        self.assertEqual(sorted(fields), sorted(self.expected_fields.keys()))

    def test_blank_fields(self):
        apps.get_model('podmin', 'podcast')
        for field in self.optional_fields:
            self.assertEqual(Podcast._meta.get_field(field).blank, True)

    ###
    # Test the properties
    ###

    def test_generator_property(self):
        pass

    def test_itunes_image_property(self):
        pass

    def test_small_image_property(self):
        pass

    def test_large_image_property(self):
        pass

    def test_medium_image_property(self):
        pass

    def test_feed_url_property(self):
        pass

    def test_unicode(self):
        pass

    ###
    # Test the save method
    ###

    def test_creation_with_only_required_fields(self):
        # just make sure a podcast is created when we supply only the
        # required fields
        podcast = Podcast.objects.create(**self.minimal_podcast)
        self.assertIsInstance(podcast, Podcast)

    def test_creation_with_all_fields(self):
        # make sure we can create a podcast with every possible field
        # specified
        podcast = Podcast.objects.create(**self.maximal_podcast)
        self.assertIsInstance(podcast, Podcast)

    def test_simple_field_defaults(self):
        # Go through the fields with static defaults and make sure they
        # get set correctly when we don't supply values
        podcast = Podcast.objects.create(**self.minimal_podcast)

        for field, value in self.field_defaults.iteritems():
            self.assertEqual(getattr(podcast, field), value)

    def test_file_urls_relative_media_url(self):
        # pub_url and storage_url can be set to urls outside of this app
        # and need to be absolute urls so we can use them as-is in feeds.
        # If the field isn't specified, we need to generate an absolute url
        # using settings.MEDIA_URL - and if MEDIA_URL is a relative url,
        # we want to create an absolute url out of it for storage_url and
        # pub_url. This tests the case where MEDIA_URL is relative, in which
        # case we should end up with an absolute url with the default Site
        # fqdn
        with self.settings(MEDIA_URL='/media/'):
            podcast = Podcast.objects.create(**self.minimal_podcast)
            self.assertEqual(
                podcast.pub_url,
                'http://example.com/media/minimal')
            self.assertEqual(
                podcast.storage_url,
                'http://example.com/media/minimal')

    def test_file_urls_absolute_media_url(self):
        # (see test above)
        # this checks that if we don't specify storage and pub urls on creation
        # they will be set to default absolute urls based on the
        # MEDIA_URL setting
        with self.settings(MEDIA_URL='http://podcast.example.com/media/'):
            podcast = Podcast.objects.create(**self.minimal_podcast)
            self.assertEqual(
                podcast.pub_url,
                'http://podcast.example.com/media/minimal')
            self.assertEqual(
                podcast.storage_url,
                'http://podcast.example.com/media/minimal')

    def test_dirs(self):
        # If pub_dir and storage_dir are not specified, make sure the storage
        # directories are set to a default path based on settings.MEDIA_ROOT
        with self.settings(MEDIA_ROOT='/tmp/podcast/'):
            podcast = Podcast.objects.create(**self.minimal_podcast)
            print('dirs')
            print(podcast.pub_dir)
            print(podcast.storage_dir)
            print('-')
            self.assertEqual(
                podcast.pub_dir,
                '/tmp/podcast/minimal')
            self.assertEqual(
                podcast.storage_dir,
                '/tmp/podcast/minimal')

    def test_buffer_dirs(self):
        pass

    def test_directory_creation(self):
        pass

    ###
    # Test publishing episodes
    ###

    def test_ripe_epsiodes_published(self):
        pass

    def test_expired_epsiodes_not_published(self):
        pass

    def test_inactive_epsiodes_not_published(self):
        pass

    def test_future_epsiodes_not_published(self):
        pass

    ###
    # Test feed generation
    ###

    def test_feed_generation(self):
        pass

    def test_feed_file_creation(self):
        pass

    def test_feed_header(self):
        pass

    def test_feed_episodes(self):
        pass

    def test_feed_file_contents(self):
        pass

    def test_published_date_updated(self):
        pass

    ###
    # Test publishing from files
    # NOTE: this method does too much, and should be refactored
    # meanwhile, test that a given set of files generates the right
    # episodes, makes a correct feed, and updates the right podcast fields
    # comprehensive tests should be created in order to refactor
    ###

    def test_publish_from_files(self):
        pass

    ###
    # Test misc model methods
    ###

    def test_transform_filename(self):
        pass

    ###
    # Test Mothballing
    ###

    def test_mothball_directory_creation(self):
        pass

    def test_mothball_file_creation(self):
        pass

    def test_mothball_file_contents(self):
        pass

    def test_mothball_image_files(self):
        pass
