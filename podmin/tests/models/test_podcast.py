# python stuff
from itertools import chain
from mock import patch, call
import shutil
import os
import time

# django stuff
from django.test import TestCase, override_settings
from django.db import models
from django_markdown.models import MarkdownField
from django.apps import apps
from django.core.files import File

# podmin stuff
from podmin.models import Podcast, Episode


###
# Test the Podcast model
###
@override_settings(MEDIA_URL='/test_media/',
                   MEDIA_ROOT='/tmp/podmin_test',
                   STATIC_ROOT='/tmp/podmin_test/static',
                   BUFFER_ROOT='/tmp/podmin_test/buffer')
class PodcastTests(TestCase):

    def setUp(self):
        # make a directory to store any file stuff we test

        if not os.path.isdir('/tmp/podmin_test'):
            os.mkdir('/tmp/podmin_test')

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
            'buffer_dir': models.CharField,
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
            'itunes_url',
            'image'
        ]

        self.required_fields = [
            'title',
            'slug',
            'language'
        ]

        self.minimal_podcast = {
            'title': 'A Minimal Podcast',
            'slug': 'minimal',
            'language': 'en'
        }

        self.maximal_podcast = {
            'title': 'A Maximal Podcast',
            'slug': 'maximal',
            'language': 'en',
            'credits': 'tests by Kennric',
            'published': None,
            'website': 'http://a.website.com',
            'frequency': 'weekly',
            'pub_url': 'http://a.website.com/rss',
            'pub_dir': '/tmp/podmin_test/maximal/rss',
            'storage_dir': '/tmp/podmin_test/maximal',
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
            'file_rename_format': "{podcast}_{number:0>2}_{date}"
        }

    def tearDown(self):
        # remove any temp files we made in /tmp/podmin_test
        if os.path.isdir('/tmp/podmin_test'):
            shutil.rmtree('/tmp/podmin_test')

    ###
    # Start the tests
    ###

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
        # make sure to update with the current version
        # as of 20170101 version is 0.3.0, name is Podmin
        podcast = Podcast.objects.create(**self.minimal_podcast)
        self.assertEqual(podcast.generator, 'Podmin 0.3beta2')

    def test_rss_image_property(self):
        # this method returns the name of the image intended for rss inclusion
        # name should be <image_name>_rss.<image_extension>

        podcast = Podcast.objects.create(**self.minimal_podcast)
        podcast.image.save(
            'test_image.png',
            File(open('podmin/static/img/default_podcast.png')))

        self.assertEqual(
            podcast.rss_image,
            u'http://example.com/test_media/minimal/img/test_image_rss.png')

    def test_itunes_image_property(self):
        # this method returns the name of the image intended for iTunes
        # name should be <image_name>_itunes.<image_extension>
        podcast = Podcast.objects.create(**self.minimal_podcast)
        podcast.image.save(
            'test_image.png',
            File(open('podmin/static/img/default_podcast.png')))

        self.assertEqual(
            podcast.itunes_image,
            u'http://example.com/test_media/minimal/img/test_image_itunes.png')

    def test_small_image_property(self):
        # this method returns the name of the small (thumbnail) image
        # name should be <image_name>_small.<image_extension>

        podcast = Podcast.objects.create(**self.minimal_podcast)
        podcast.image.save(
            'test_image.png',
            File(open('podmin/static/img/default_podcast.png')))

        self.assertEqual(
            podcast.small_image,
            u'http://example.com/test_media/minimal/img/test_image_small.png')

    def test_large_image_property(self):
        # this method returns the name of the large sized image
        # name should be <image_name>_small.<image_extension>

        podcast = Podcast.objects.create(**self.minimal_podcast)
        podcast.image.save(
            'test_image.png',
            File(open('podmin/static/img/default_podcast.png')))

        self.assertEqual(
            podcast.large_image,
            u'http://example.com/test_media/minimal/img/test_image_large.png')

    def test_medium_image_property(self):
        # this method returns the name of the medium sized image
        # name should be <image_name>_small.<image_extension>

        podcast = Podcast.objects.create(**self.minimal_podcast)
        podcast.image.save(
            'test_image.png',
            File(open('podmin/static/img/default_podcast.png')))

        self.assertEqual(
            podcast.medium_image,
            u'http://example.com/test_media/minimal/img/test_image_medium.png')

    def test_feed_url_property(self):
        # this method should return a full URL to the rss feed file
        # this should be composed of the pub_url and feed filename

        podcast = Podcast.objects.create(**self.minimal_podcast)
        self.assertEqual(
            podcast.feed_url,
            u'http://example.com/test_media/minimal/rss.xml')

    def test_unicode(self):
        podcast = Podcast.objects.create(**self.minimal_podcast)

        self.assertEqual(unicode(podcast), u'A Minimal Podcast')

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

    def test_default_image(self):
        # if we don't specify an image, make sure the default image is added
        podcast = Podcast.objects.create(**self.minimal_podcast)
        self.assertEqual(podcast.image.name, 'minimal/img/default_image.png')

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

    def test_media_dirs(self):
        # If pub_dir and storage_dir are not specified, make sure the storage
        # directories are set to a default path based on settings.MEDIA_ROOT

        podcast = Podcast.objects.create(**self.minimal_podcast)
        self.assertEqual(
            podcast.pub_dir,
            '/tmp/podmin_test/minimal')
        self.assertEqual(
            podcast.storage_dir,
            '/tmp/podmin_test/minimal')

    def test_buffer_dir(self):
        # If buffer_dir is not specified, make sure the buffer directory is
        # set to a default path based on settings.BUFFER_ROOT

        podcast = Podcast.objects.create(**self.minimal_podcast)
        self.assertEqual(
            podcast.buffer_dir,
            '/tmp/podmin_test/buffer/minimal')

    """
    #### this test is replaced with simple directory creation tests,
    #### since mocking gets very messy with how many components in the
    #### model copy, read, ters/make directories, etc. Maybe later we can mock
    #### all filesytem operations in a sane way and switch back to this

    # mock the os methods for creating and testing directories - we mock
    # that 'isdir' returns false to ensure the code tries to make the dirs
    @patch('podmin.models.os.path.isdir')
    @patch('podmin.models.os.makedirs')
    def test_storage_directory_creation(self, mock_makedirs, mock_isdir):
        # for all the directories we need, make sure they get created on save
        # these are:
        # <storage_dir>/audio
        # <storage_dir>/img
        # <buffer_dir>/audio
        # <buffer_dir>/img
        mock_isdir.return_value = False

        Podcast.objects.create(**self.minimal_podcast)

        calls = [call('/tmp/podmin_test/minimal/img'),
                 call('/tmp/podmin_test/minimal/audio'),
                 call('/tmp/podmin_test/buffer/minimal/img'),
                 call('/tmp/podmin_test/buffer/minimal/audio')]

        mock_makedirs.assert_has_calls(calls)
    """

    def test_storage_directory_creation(self):
        # for all the directories we need, make sure they get created on save
        # these are:
        # <storage_dir>/audio
        # <storage_dir>/img
        # <buffer_dir>/audio
        # <buffer_dir>/img

        Podcast.objects.create(**self.minimal_podcast)

        self.assertTrue(os.path.isdir('/tmp/podmin_test/minimal/img'))
        self.assertTrue(os.path.isdir('/tmp/podmin_test/minimal/audio'))
        self.assertTrue(os.path.isdir('/tmp/podmin_test/buffer/minimal/img'))
        self.assertTrue(os.path.isdir('/tmp/podmin_test/buffer/minimal/audio'))


    ###
    # Test misc model methods
    ###

    def test_transform_filename_default_regex(self):
        # using the default pattern, this method transforms a given filename
        # the default transformation pattern is {podcast}_{number:0>2}_{date}
        # since this is the podcast model's transformation method, it is really
        # only useful for renaming cover art. A podcast object doesn't have a
        # number, guid, track number, episode slug, or part, so the method
        # transforms those as "" except for 'number' which is replaced by the
        # string "cover"

        podcast = Podcast.objects.create(**self.minimal_podcast)

        # we have to set the rename_files field first
        podcast.rename_files = True
        podcast.save()

        test_filename = 'testo.jpg'
        date_now = time.strftime("%Y%m%d")

        # remember 'number' -> 'cover'
        expected_filename = "minimal_cover_{0}.jpg".format(date_now)

        new_filename = podcast.transform_filename(test_filename)
        self.assertEqual(expected_filename, new_filename)

    def test_transform_filename_bad_pattern(self):
        # what happens if we have put something that isn't a real pattern in
        # the file_rename_format field? The method should log the error and
        # return the original filename unchanged
        podcast = Podcast.objects.create(**self.minimal_podcast)

        # we have to set the rename_files field first
        podcast.rename_files = True
        podcast.file_rename_format = "StringWithNoPlaceholders"
        podcast.save()

        test_filename = 'testo.jpg'
        new_filename = podcast.transform_filename(test_filename)

        self.assertEqual(test_filename, new_filename)

    def test_transform_filename_good_pattern(self):
        # available filename substitution parameters for podcasts are
        # podcast, tags, org, author and date. if the podcast does not have
        # tags, org, or author, those default to empty strings. Further
        # 'number' transforms to "cover" and episode, track_number, guid, and
        # part are replaced with empty strings
        podcast = Podcast.objects.create(**self.minimal_podcast)
        test_filename = 'testo.jpg'
        date_now = time.strftime("%Y%m%d")

        # we have to set the rename_files field first
        podcast.rename_files = True

        # lets check that all the always-empty strings work
        pattern = "episode{episode}_track{track_number}_guid{guid}_part{part}"
        podcast.file_rename_format = pattern
        podcast.save()

        expected_filename = "episode_track_guid_part.jpg"
        new_filename = podcast.transform_filename(test_filename)

        self.assertEqual(expected_filename, new_filename)

        # now lets check the unset fields default to blank strings
        pattern = "tags{tags}_org{org}_author{author}"
        podcast.file_rename_format = pattern
        podcast.save()

        expected_filename = "tags_org_author.jpg"
        new_filename = podcast.transform_filename(test_filename)

        self.assertEqual(expected_filename, new_filename)

        # lets make sure number->'cover' and date is always the current date
        pattern = "{number}_{date}"
        podcast.file_rename_format = pattern
        podcast.save()

        expected_filename = "cover_{0}.jpg".format(date_now)
        new_filename = podcast.transform_filename(test_filename)

        self.assertEqual(expected_filename, new_filename)

        # now lets set some tags, an author, and and org, and make sure those
        # work, along with the podcast slug.
        # NOTE: non-word chars in fields should -> _
        pattern = "{podcast}_{tags}_{org}_{author}"
        podcast.file_rename_format = pattern
        podcast.tags = 'tag1,tag2,tag3'
        podcast.organization = 'WKRP'
        podcast.author = 'Pam Testo'
        podcast.save()

        expected_filename = "minimal_tag1_tag2_tag3_WKRP_Pam_Testo.jpg"
        new_filename = podcast.transform_filename(test_filename)

        self.assertEqual(expected_filename, new_filename)

    def test_do_not_transform_filename(self):
        podcast = Podcast.objects.create(**self.minimal_podcast)

        # rename_files should be false here, but let's make sure
        podcast.rename_files = False
        podcast.save()

        test_filename = 'testo.jpg'
        new_filename = podcast.transform_filename(test_filename)

        self.assertEqual(test_filename, new_filename)

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
