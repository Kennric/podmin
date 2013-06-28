from django.forms import ModelForm, FileField, BooleanField
from podmin.models import Episode, Podcast


class EpisodeForm(ModelForm):
    upload_file = FileField()
    tag_audio = BooleanField()

    class Meta:
        model = Episode
        exclude = ('podcast', 'filename', 'pub_date', 'size', 'length')


class PodcastForm(ModelForm):
    class Meta:
        model = Podcast
        exclude = ('updated', 'last_import', 'combine_segments',
                   'publish_segments', 'tmp_dir', 'up_dir', 'cleaner')
