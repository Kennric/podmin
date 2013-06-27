from django.forms import ModelForm
from podmin.models import Episode, Podcast

class EpisodeForm(ModelForm):
    class Meta:
        model = Episode

class PodcastForm(ModelForm):
    class Meta:
        model = Podcast
