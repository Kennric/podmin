from django.forms import ModelForm, FileField, BooleanField, DateTimeField, CharField
from django.forms.widgets import SplitDateTimeWidget
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
                  'guid', 'part', 'current', 'filename', 'upload_file',
                  'rename_file', 'tag_audio', 'show_notes']
        exclude = ('podcast', 'size', 'length')


class PodcastForm(ModelForm):
    class Meta:
        model = Podcast
        exclude = ('updated', 'last_import', 'combine_segments',
                   'publish_segments', 'up_dir', 'cleaner')
