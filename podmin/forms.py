from django.forms import (FileField, DateTimeField, CharField, TextInput,
                          Textarea, EmailInput, FileInput, ImageField, Select,
                          ChoiceField, IntegerField, NullBooleanSelect,
                          CheckboxInput, ModelMultipleChoiceField,
                          SelectMultiple, RadioSelect, SplitDateTimeWidget)
from form_utils.forms import BetterModelForm
from form_utils.widgets import ImageWidget

from podmin.models import Episode, Podcast, Category
import datetime
from django.db.models import Count
from constants import *


class EpisodeForm(BetterModelForm):
    title = CharField(
        label='Title',
        widget=TextInput(
            attrs={'class': 'input',
                   'type': 'text',
                   'placeholder': 'Episode Title'}))

    subtitle = CharField(
        label='Subtitle',
        required=False,
        widget=TextInput(
            attrs={'class': 'input',
                   'type': 'text',
                   'placeholder': 'Episode Subtitle'}))

    number = CharField(
        label='Episode Number',
        required=False,
        widget=TextInput(attrs={'class': 'input', 'type': 'text'}))

    guid = CharField(
        label='GUID',
        widget=TextInput(attrs={'class': 'input', 'type': 'text'}))

    description = CharField(
        label='Episode Description',
        required=False,
        widget=Textarea(
            attrs={'class': 'input textarea',
                   'type': 'text',
                   'rows': 3}))

    buffer_image = FileField(
        label='Episode Image',
        required=False,
        widget=FileInput(attrs={'class': 'input', 'type': 'file'}))

    pub_date = DateTimeField(
        label='Publication Date',
        initial=datetime.datetime.today,
        widget=TextInput(attrs={'class': 'input datetimepicker',
                                'type': 'text'}))
    tags = CharField(
        label='Tags',
        required=False,
        widget=TextInput(attrs={'class': 'input', 'type': 'text'}))

    active = ChoiceField(
        label='Ready to Publish?',
        widget=Select(attrs={'class': 'input inline'}),
        choices=BOOLEAN_CHOICES,
        initial=BOOLEAN_CHOICES[0][0],
        help_text='Is the episode ready to go live?')

    buffer_audio = FileField(
        label='Episode Audio',
        required=False,
        widget=FileInput(attrs={'class': 'input', 'type': 'file'}))

    show_notes = CharField(
        label='Show Notes',
        required=False,
        widget=Textarea(attrs={'class': 'input textarea',
                               'type': 'text',
                               'rows': 5}),
        help_text='Notes about this episode')

    credits = CharField(
        label='Credits',
        required=False,
        widget=Textarea(attrs={'class': 'input textarea',
                               'type': 'text',
                               'rows': 3}),
        help_text='Art and Music Credits')

    guests = CharField(
        label='Guests',
        required=False,
        widget=Textarea(attrs={'class': 'input textarea',
                               'type': 'text',
                               'rows': 3}),
        help_text='Guests appearing in this episode')


    class Meta:
        model = Episode
        fields = ['title', 'subtitle', 'number', 'guid', 'description',
                  'buffer_image', 'pub_date', 'tags', 'active',
                  'buffer_audio', 'show_notes', 'credits', 'guests']

        exclude = ('podcast', 'size', 'length', 'part', 'mime_type')


class PodcastForm(BetterModelForm):

    """
    Start with the common fields
    """
    title = CharField(
        label='Title',
        widget=TextInput(
            attrs={'class': 'input',
                   'type': 'text',
                   'placeholder': 'Podcast Title'}))

    slug = CharField(
        label='Slug',
        widget=TextInput(
            attrs={'class': 'input slug',
                   'type': 'text'}),
        help_text='Only letters, numbers, and -')

    subtitle = CharField(
        label='Subtitle',
        required=False,
        widget=TextInput(
            attrs={'class': 'input',
                   'type': 'text',
                   'placeholder': 'Podcast Subtitle'}))

    description = CharField(
        label='Description',
        required=False,
        widget=Textarea(attrs={'class': 'input textarea',
                               'type': 'text',
                               'rows': 3}))

    language = ChoiceField(
        label='Language',
        widget=Select(attrs={'class': 'input inline'}),
        choices=LANGUAGE_CHOICES)

    explicit = ChoiceField(
        label='Contains Explicit Material',
        widget=Select(attrs={'class': 'input inline'}),
        choices=EXPLICIT_CHOICES,
        initial=EXPLICIT_CHOICES[1][0])

    tags = CharField(
        label='Tags',
        required=False,
        widget=TextInput(attrs={
            'class': 'input',
            'type': 'text',
            'placeholder': 'Comma-separated list of tags.'}))

    itunes_categories = ModelMultipleChoiceField(
      queryset=Category.objects.annotate(
        num_cats=Count('category')).filter(num_cats__lt=1).order_by('parent'),
      label='iTunes Categories',
      required=False,
      widget=SelectMultiple(attrs={'class': 'input taller', 'size': 10}))

    author = CharField(
        label='Author Name',
        widget=TextInput(attrs={'class': 'input', 'type': 'text'}))

    contact = CharField(
        label='Author Email',
        widget=EmailInput(attrs={'class': 'input', 'type': 'email'}))

    image = FileField(
        label='Podcast Image',
        required=False,
        widget=FileInput(attrs={'class': 'input', 'type': 'file'}),
        help_text='Minimum 1400x1400 RGB PNG or JPEG')

    website = CharField(
        label='Podcast Website',
        required=False,
        widget=TextInput(attrs={'class': 'input', 'type': 'url'}),
        help_text="URL to this podcast's home page")

    credits = CharField(
        label='Art and Music Credits',
        required=False,
        widget=Textarea(attrs={'class': 'input textarea',
                               'type': 'text',
                               'rows': 3}),
        help_text='One contributer per line.')

    frequency = ChoiceField(
        label='Publishing Frequency',
        widget=Select(attrs={'class': 'input'}),
        choices=FREQUENCY_CHOICES)

    license = ChoiceField(
        label='License',
        widget=Select(attrs={'class': 'input'}),
        choices=LICENSE_CHOICES)

    feed_format = ChoiceField(
        label='Feed Type',
        widget=Select(attrs={'class': 'input'}),
        choices=FEED_TYPE_CHOICES,
        initial=FEED_TYPE_CHOICES[1][0],
        help_text='Type of feed to publish.')

    organization = CharField(
        label='Organization',
        required=False,
        widget=TextInput(attrs={'class': 'input', 'type': 'text'}))

    station = CharField(
        label='Radio Station',
        required=False,
        widget=TextInput(attrs={'class': 'input', 'type': 'text'}))

    copyright = CharField(
        label='Copyright',
        required=False,
        widget=TextInput(attrs={'class': 'input'}))

    ttl = IntegerField(
        label='Minutes this feed can be cached',
        initial=1440,
        widget=TextInput(attrs={'class': 'input'}))

    max_age = IntegerField(
        label='Days to keep an episode',
        initial=365,
        widget=TextInput(attrs={'class': 'input'}))

    editor_name = CharField(
        label='Editor Name',
        required=False,
        widget=TextInput(attrs={'class': 'input'}))

    editor_email = CharField(
        label='Editor Email',
        required=False,
        widget=TextInput(attrs={'class': 'input'}))

    webmaster_name = CharField(
        label='Webmaster name',
        required=False,
        widget=TextInput(attrs={'class': 'input'}))

    webmaster_email = CharField(
        label='Webmaster Email',
        required=False,
        widget=TextInput(attrs={'class': 'input'}))

    block = ChoiceField(
        label='Block',
        widget=Select(attrs={'class': 'input inline'}),
        choices=BOOLEAN_CHOICES,
        initial=BOOLEAN_CHOICES[0][0],
        help_text='Disable this podcast in iTunes.')

    rename_files = ChoiceField(
        label='Rename Files',
        widget=Select(attrs={'class': 'input inline'}),
        choices=BOOLEAN_CHOICES,
        initial=BOOLEAN_CHOICES[0][0],
        help_text='Rename audio files with slug and date.')

    tag_audio = ChoiceField(
        label='Tag Audio',
        widget=Select(attrs={'class': 'input inline'}),
        choices=BOOLEAN_CHOICES,
        initial=BOOLEAN_CHOICES[1][0],
        help_text='Tag audio file with podcast/episode details.')

    pub_url = CharField(
        label='Publication (rss) URL',
        required=False,
        widget=TextInput(attrs={'class': 'input'}))

    storage_url = CharField(
        label='File Storage URL',
        required=False,
        widget=TextInput(attrs={'class': 'input'}))

    itunes_url = CharField(
        label='iTunes URL',
        required=False,
        widget=TextInput(attrs={'class': 'input'}))

    feedburner_url = CharField(
        label='FeedBurner URL',
        required=False,
        widget=TextInput(attrs={'class': 'input'}))

    tmp_dir = CharField(
        label='Temporary Directory',
        initial='/tmp',
        widget=TextInput(attrs={'class': 'input'}))

    up_dir = CharField(
        label='Upload Directory',
        required=False,
        widget=TextInput(attrs={'class': 'input'}))

    cleaner = CharField(
        label='Cleaner',
        required=False,
        widget=TextInput(attrs={'class': 'input'}))

    combine_segments = ChoiceField(
        label='Combine Segments',
        widget=Select(attrs={'class': 'input inline'}),
        choices=BOOLEAN_CHOICES,
        initial=BOOLEAN_CHOICES[0][0])

    publish_segments = ChoiceField(
        label='Publish Segments',
        widget=Select(attrs={'class': 'input inline'}),
        choices=BOOLEAN_CHOICES,
        initial=BOOLEAN_CHOICES[0][0])


    def __init__(self, *args, **kwargs):
        super(PodcastForm, self).__init__(*args, **kwargs)

        category_choices = []

        for category in Category.objects.all():
            new_category = []
            sub_categories = []

            if not category.parent:
                if len(category.category_set.all()) > 0:
                    for sub_category in category.category_set.all():
                        sub_categories.append([sub_category.id,
                                               sub_category.name])
                    new_category = [category.name, sub_categories]
                else:
                    new_category = [category.id, category.name]
                category_choices.append(new_category)

        self.fields['itunes_categories'].choices = category_choices

    class Meta:
        model = Podcast

        fieldsets = [
            ('main',
                {'fields': ['title', 'slug', 'subtitle', 'description',
                            'author', 'contact', 'image', 'frequency',
                            'language', 'explicit', 'itunes_categories',
                            'tags', 'copyright', 'license'],
                 'legend': 'Required Settings',
                 'classes': ['required', 'drawer', 'active']}),
            ('Optional',
                {'fields': ['editor_name', 'editor_email', 'organization',
                            'website', 'station', 'credits',
                            'feedburner_url', 'webmaster_name',
                            'webmaster_email', 'block',
                            'rename_files', 'tag_audio', 'itunes_url'],
                 'legend': 'Optional Settings',
                 'classes': ['optional', 'collapse', 'drawer']}),
            ('Advanced',
                {'fields': ['feed_format', 'ttl', 'max_age', 'pub_url',
                            'storage_url', 'tmp_dir', 'combine_segments',
                            'publish_segments', 'up_dir', 'cleaner'],
                 'legend': 'Advanced Settings',
                 'description': """Don't change these unless you know
                                   what you are doing.""",
                 'classes': ['advanced', 'collapse', 'drawer']})
            ]
