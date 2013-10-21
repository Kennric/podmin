from django.forms import (ModelForm, FileField, BooleanField, DateTimeField,
                          CharField)
# from django.forms.widgets import SplitDateTimeWidget
from podmin.models import Episode, Podcast
import datetime


class EpisodeForm(ModelForm):
    filename = CharField(required=False, label='Current File')
    upload_file = FileField(required=False, label='Upload new file')
    tag_audio = BooleanField(required=False)
    rename_file = BooleanField(required=False)
    pub_date = DateTimeField(label='Publication Date',
                             initial=datetime.datetime.today)

    class Meta:
        model = Episode
        fields = ['title', 'subtitle', 'description', 'pub_date', 'tags',
                  'guid', 'part', 'active', 'filename', 'upload_file',
                  'rename_file', 'tag_audio', 'show_notes']
        exclude = ('podcast', 'size', 'length')


class PodcastForm(ModelForm):

    class Meta:
        model = Podcast

        fields = ('title', 'subtitle', 'description', 'keywords', 'tags', 
                  'summary', 'author', 'contact', 'image', 'website',
                  'organization', 'station', 'credits', 'frequency',
                  'license', 'copyright', 'copyright_url', 'language',
                  'domain', 'feedburner', 'ttl',  'max_age', 'editor_email',
                  'webmaster_email', 'explicit', 'itunes_categories',
                  'explicit', 'block', 'pub_url', 'itunes', 'rename_files',
                  'pub_dir', 'storage_dir', 'storage_url', 'tmp_dir')

        exclude = ('owner', 'slug', 'last_import', 'combine_segments',
                   'publish_segments', 'up_dir', 'cleaner', 'updated',
                   'redirect', 'created', 'updated')