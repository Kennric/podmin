from django.forms import ModelForm, FileField, BooleanField, DateTimeField
from django.forms.widgets import SplitDateTimeWidget
from podmin.models import Episode, Podcast
import datetime

class EpisodeForm(ModelForm):
    upload_file = FileField()
    tag_audio = BooleanField(required=False)
    rename_file = BooleanField(required=False)
    pub_date = DateTimeField(initial=datetime.date.today)

    class Meta:
        model = Episode
        exclude = ('podcast', 'filename', 'size', 'length')
        widgets = {'pub_date': SplitDateTimeWidget()}


class PodcastForm(ModelForm):
    class Meta:
        model = Podcast
        exclude = ('updated', 'last_import', 'combine_segments',
                   'publish_segments', 'up_dir', 'cleaner')
