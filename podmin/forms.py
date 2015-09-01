from django.forms import (ModelForm, FileField, BooleanField,
                          SplitDateTimeField,
                          CharField, TextInput, Textarea, EmailInput,
                          FileInput, ImageField, Select, ChoiceField,
                          IntegerField, NullBooleanSelect, CheckboxInput,
                          ModelMultipleChoiceField, SelectMultiple,
                          RadioSelect, SplitDateTimeWidget)

from podmin.models import Episode, Podcast, Category
import datetime
from django.db.models import Count
from constants import *


class EpisodeForm(ModelForm):
    title = CharField(
        label='Title',
        widget=TextInput(
            attrs={'class': 'input',
                   'type': 'text',
                   'placeholder': 'Episode Title'}))

    subtitle = CharField(
        label='Subtitle',
        widget=TextInput(
            attrs={'class': 'input',
                   'type': 'text',
                   'placeholder': 'Episode Subtitle'}))

    number = CharField(label='Episode Number',
                       widget=TextInput(attrs={'class': 'input',
                                               'type': 'text'}))

    guid = CharField(label='GUID',
                     widget=TextInput(attrs={'class': 'input',
                                             'type': 'text'}))
    description = CharField(
        label='Episode Description',
        widget=Textarea(
            attrs={'class': 'input textarea',
                   'type': 'text',
                   'rows': 5}),
        help_text='AKA Summary')

    buffer_image = ImageField(label='Episode Image', required=False,
                              widget=FileInput(attrs={'class': 'input',
                                                      'type': 'file'}))

    pub_date = SplitDateTimeField(label='Publication Date',
                                  initial=datetime.datetime.today,
                                  widget=SplitDateTimeWidget(
                                  attrs={'class': 'input','type': 'text'}))

    tags = CharField(label='Tags', required=False,
                     widget=TextInput(attrs={'class': 'input',
                                             'type': 'text'}))

    active = BooleanField(label='Active', required=False,
                          widget=CheckboxInput(attrs={'class': 'checkbox'}))

    buffer_audio = FileField(label='Episode Audio', required=True,
                             widget=FileInput(attrs={'class': 'input',
                                                     'type': 'file'}))

    show_notes = CharField(label='Show Notes',
                           widget=Textarea(
                              attrs={'class': 'input textarea',
                                     'type': 'text',
                                     'rows': 5}),
                           help_text='Notes about this episode')

    credits = CharField(label='Credits',
                        widget=Textarea(
                            attrs={'class': 'input textarea',
                                   'type': 'text',
                                   'rows': 5}),
                        help_text='Art and Music Credits')

    guests = CharField(label='Guests',
                       widget=Textarea(attrs={'class': 'input textarea',
                                              'type': 'text',
                                              'rows': 5}),
                       help_text='Guests appearing in this episode')

    class Meta:
        model = Episode
        fields = ['title', 'subtitle', 'number', 'guid', 'description',
                  'buffer_image',
                  'pub_date', 'tags', 'active', 'buffer_audio', 'show_notes',
                  'credits', 'guests']

        exclude = ('podcast', 'size', 'length', 'part', 'mime_type')


class PodcastForm(ModelForm):

    """
    Start with the common fields
    """
    title = CharField(
        label='Title',
        widget=TextInput(
            attrs={'class': 'wide input',
                   'type': 'text',
                   'placeholder': 'Podcast Title'}))

    slug = CharField(
        label='Slug',
        widget=TextInput(
            attrs={'class': 'narrow input slug',
                   'type': 'text'}),
        help_text='Only letters, numbers, and -')

    subtitle = CharField(
        label='Subtitle',
        widget=TextInput(
            attrs={'class': 'input',
                   'type': 'text',
                   'placeholder': 'Podcast Subtitle'}))

    description = CharField(
        label='Podcast Description',
        widget=Textarea(attrs={'class': 'input textarea',
                               'type': 'text',
                               'rows': 5}),
        help_text='In iTunes, this is the Summary')

    language = ChoiceField(label='Podcast Language',
                           widget=Select(attrs={'class': 'input inline'}),
                           choices=LANGUAGE_CHOICES)

    explicit = ChoiceField(label='Contains Explicit Material',
                           widget=Select(attrs={'class': 'input inline'}),
                           choices=EXPLICIT_CHOICES,
                           help_text='Is this for adults only?')

    tags = CharField(label='Tags', required=False,
                     widget=TextInput(attrs={'class': 'input',
                                             'type': 'text'}),
                     help_text='Comma-separated list of arbitrary tags.')

    itunes_categories = ModelMultipleChoiceField(
      queryset=Category.objects.annotate(num_cats=Count('category')).filter(
        num_cats__lt=1).order_by('parent'),
      label='iTunes Categories', required=False,
      widget=SelectMultiple(attrs={'class': 'input taller', 'size': 10}))

    author = CharField(label='Author Name', required=False,
                       widget=TextInput(attrs={'class': 'wide input',
                                               'type': 'text'}))
    contact = CharField(label='Author Email', required=False,
                        widget=EmailInput(attrs={'class': 'wide input',
                                                 'type': 'email'}))
    image = ImageField(label='Podcast Image', required=False,
                       widget=FileInput(attrs={'class': 'wide input',
                                               'type': 'file'}),
                       help_text='Minimum 1400x1400 RGB PNG or JPEG')
    website = CharField(label='Podcast Website', required=False,
                        widget=TextInput(attrs={'class': 'wide input',
                                                'type': 'url'}),
                        help_text="URL to this podcast's home page")

    credits = CharField(label='Art and Music Credits', required=False,
                        widget=Textarea(attrs={'class': 'input textarea',
                                               'type': 'text',
                                               'rows': 5}),
                        help_text='One contributer per line.')

    frequency = ChoiceField(label='Publishing Frequency',
                            widget=Select(attrs={'class': 'input'}),
                            choices=FREQUENCY_CHOICES)

    license = ChoiceField(label='Podcast License',
                          widget=Select(attrs={'class': 'input'}),
                          choices=LICENSE_CHOICES)
    """
    Now the advanced settings - these must be optional or have
    reasonable defaults
    """

    feed_format = ChoiceField(label='Feed Type',
                              widget=Select(attrs={'class': 'input'}),
                              choices=FEED_TYPE_CHOICES,
                              help_text='Type of feed to publish.')

    organization = CharField(label='Organization', required=False,
                             widget=TextInput(attrs={'class': 'narrow input',
                                                     'type': 'text'}))
    station = CharField(label='Radio Station', required=False,
                        widget=TextInput(attrs={'class': 'narrow input',
                                                'type': 'text'}))
    copyright = CharField(label='Copyright',
                          required=False,
                          widget=TextInput(attrs={'class': 'wide input'}))
    ttl = IntegerField(label='Minutes this feed can be cached',
                       initial=1440,
                       widget=TextInput(attrs={'class': 'xnarrow input'}))
    max_age = IntegerField(label='Days to keep an episode',
                           initial=365,
                           widget=TextInput(attrs={'class': 'xnarrow input'}))
    editor_email = CharField(label='Editor Email', required=False,
                             widget=TextInput(attrs={'class': 'input'}))
    webmaster_email = CharField(label='Webmaster Email', required=False,
                                widget=TextInput(
                                  attrs={'class': 'wide input'}))
    block = BooleanField(label='Blocked', required=False,
                         widget=CheckboxInput(attrs={'class': 'checkbox'}))

    rename_files = BooleanField(label='Rename File', required=False,
                                widget=CheckboxInput(
                                  attrs={'class': 'checkbox'}))
    tag_audio = BooleanField(label='Tag Audio File', required=False,
                             widget=CheckboxInput(attrs={'class': 'checkbox'}))
    pub_url = CharField(label='Publication (rss) URL',
                        required=False,
                        widget=TextInput(attrs={'class': 'wide input'}))

    storage_url = CharField(label='File Storage URL',
                            required=False,
                            widget=TextInput(attrs={'class': 'wide input'}))

    itunes_url = CharField(label='iTunes URL', required=False,
                           widget=TextInput(attrs={'class': 'wide input'}))

    tmp_dir = CharField(label='Temporary Directory',
                        initial='/tmp',
                        widget=TextInput(attrs={'class': 'wide input'}))

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

        fields = ('title', 'slug', 'subtitle', 'description', 'keywords',
                  'tags',
                  'summary', 'author', 'contact', 'image', 'website',
                  'organization', 'station', 'credits', 'frequency',
                  'copyright', 'license', 'feed_format', 'language',
                  'feedburner_url', 'ttl',  'max_age', 'editor_email',
                  'webmaster_email', 'explicit', 'itunes_categories',
                  'explicit', 'block', 'rename_files', 'tag_audio',
                  'pub_url', 'storage_url', 'itunes_url', 'rename_files',
                  'tmp_dir')

        exclude = ('owner', 'copyright_url', 'last_import', 'combine_segments',
                   'publish_segments', 'summary', 'up_dir', 'cleaner',
                   'updated', 'redirect', 'created', 'updated',
                   'feedburner_url', 'keywords')
