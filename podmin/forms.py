from django.forms import (ModelForm, FileField, BooleanField, DateTimeField,
                          CharField, TextInput, Textarea, EmailInput,
                          FileInput, ImageField, Select, ChoiceField,
                          IntegerField, NullBooleanSelect, CheckboxInput,
                          ModelMultipleChoiceField, SelectMultiple,
                          RadioSelect, SplitDateTimeWidget)
#from django.forms.widgets import TextInput
from podmin.models import Episode, Podcast, Category
import datetime
from django.conf import settings
from django.db.models import Count


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

    image = ImageField(label='Episode Image', required=False,
                       widget=FileInput(attrs={'class': 'input',
                                               'type': 'file'}))

    pub_date = DateTimeField(label='Publication Date',
                             initial=datetime.datetime.today,
                             widget=SplitDateTimeWidget(
                                attrs={'class': 'input','type': 'text'}))

    tags = CharField(label='Tags',required=False,
                     widget=TextInput(attrs={'class': 'input',
                                             'type': 'text'}))

    active = BooleanField(label='Active', required=False,
        widget=CheckboxInput(attrs={'class': 'checkbox'}))

    audio = FileField(label='Episode Audio', required=True,
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
                           widget=Textarea(
                              attrs={'class': 'input textarea',
                                      'type': 'text',
                                      'rows': 5}),
                           help_text='Guests appearing in this episode')

    class Meta:
        model = Episode
        fields = ['title', 'subtitle', 'number', 'guid', 'description',
                  'image',
                  'pub_date', 'tags', 'active', 'audio', 'show_notes',
                  'credits', 'guests']

        exclude = ('podcast', 'size', 'length', 'part', 'mime_type')


class PodcastForm(ModelForm):

    title = CharField(
        label='Title',
        widget=TextInput(
            attrs={'class': 'input',
                   'type': 'text',
                   'placeholder': 'Podcast Title'}))

    subtitle = CharField(
        label='Subtitle',
        widget=TextInput(
            attrs={'class': 'input',
                   'type': 'text',
                   'placeholder': 'Podcast Subtitle'}))

    description = CharField(
        label='Podcast Description',
        widget=Textarea(
            attrs={'class': 'input textarea',
                    'type': 'text',
                    'rows': 5}),
        help_text='In iTunes, this is the Summary')

    tags = CharField(label='Tags',required=False,
                     widget=TextInput(attrs={'class': 'input',
                                             'type': 'text'}))
    author = CharField(label='Author Name', required=False,
                       widget=TextInput(attrs={'class': 'input',
                                               'type': 'text'}))
    contact = CharField(label='Author Email', required=False,
                        widget=EmailInput(attrs={'class': 'input',
                                                 'type': 'email'}))
    image = ImageField(label='Podcast Image', required=False,
                       widget=FileInput(attrs={'class': 'input',
                                              'type': 'file'}))
    website = CharField(label='Podcast Website', required=False,
                        widget=TextInput(attrs={'class': 'input',
                                                'type': 'url'}))
    organization = CharField(label='Organization', required=False,
                            widget=TextInput(attrs={'class': 'input',
                                                    'type': 'text'}))
    station = CharField(label='Radio Station', required=False,
                        widget=TextInput(attrs={'class': 'input',
                                                'type': 'text'}))
    credits = CharField(label='Art and Music Credits', required=False,
                        widget=Textarea(attrs={'class': 'input textarea',
                                               'type': 'text',
                                               'rows': 5}))
    frequency = ChoiceField(label='Publishing Frequency',
                            widget=Select(attrs={'class': 'input'}),
                            choices=settings.FREQUENCY_CHOICES)
    licence = ChoiceField(label='Podcast License',
                          widget=Select(attrs={'class': 'input'}),
                          choices=settings.LICENSE_CHOICES)
    copyright = CharField(label='Copyright',
                          required=False,
                          widget=TextInput(attrs={'class': 'input'}))
    language = CharField(label='Podcast Language',
                         widget=TextInput(attrs={'class': 'input'}))
    ttl = IntegerField(label='Minutes this feed can be cached',
                       initial=1440,
                       widget=TextInput(attrs={'class': 'input'}))
    max_age = IntegerField(label='Days to keep an episode',
                           initial=365,
                           widget=TextInput(attrs={'class': 'input'}))
    editor_email = CharField(label='Editor Email', required=False,
                             widget=TextInput(attrs={'class': 'input'}))
    webmaster_email = CharField(label='Webmaster Email', required=False,
                                widget=TextInput(attrs={'class': 'input'}))

    explicit = ChoiceField(label='Contains Explicit Material',
                           widget=Select(attrs={'class': 'input inline'}),
                           choices=settings.EXPLICIT_CHOICES)

    itunes_categories = ModelMultipleChoiceField(
      queryset=Category.objects.annotate(num_cats=Count('category')).filter(
        num_cats__lt=1).order_by('parent'),
      label='iTunes Categories', required=False,
      widget=SelectMultiple(attrs={'class': 'input taller', 'size': 10}))

    block = BooleanField(label='Blocked', required=False,
      widget=CheckboxInput(attrs={'class': 'checkbox'}))

    rename_files = BooleanField(label='Rename File', required=False,
        widget=CheckboxInput(attrs={'class': 'checkbox'}))

    tag_audio = BooleanField(label='Tag Audio File', required=False,
        widget=CheckboxInput(attrs={'class': 'checkbox'}))

    pub_url = CharField(label='Publication (rss) URL',
                        required=False,
                        widget=TextInput(attrs={'class': 'input'}))

    itunes_url = CharField(label='iTunes URL', required=False,
                           widget=TextInput(attrs={'class': 'input'}))

    pub_dir = CharField(label='Publication Directory',
                        required=False,
                        widget=TextInput(attrs={'class': 'input'}))
    storage_dir = CharField(label='File Storage Directory',
                            required=False,
                            widget=TextInput(attrs={'class': 'input'}))
    storage_url = CharField(label='File Storage URL',
                            required=False,
                            widget=TextInput(attrs={'class': 'input'}))
    tmp_dir = CharField(label='Temporary Directory',
                        initial='/tmp',
                        widget=TextInput(attrs={'class': 'input'}))
    buffer_dir = CharField(label='File Buffer Directory',
                            required=False,
                            widget=TextInput(attrs={'class': 'input'}))
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

        fields = ('title', 'subtitle', 'description', 'keywords', 'tags',
                  'summary', 'author', 'contact', 'image', 'website',
                  'organization', 'station', 'credits', 'frequency',
                  'copyright', 'license', 'language',
                  'feedburner_url', 'ttl',  'max_age', 'editor_email',
                  'webmaster_email', 'explicit', 'itunes_categories',
                  'explicit', 'block', 'rename_files', 'tag_audio',
                  'pub_url', 'itunes_url', 'rename_files', 'pub_dir',
                  'storage_dir', 'storage_url', 'tmp_dir', 'buffer_dir')

        exclude = ('owner', 'copyright_url', 'slug', 'last_import', 'combine_segments',
                   'publish_segments', 'summary', 'up_dir', 'cleaner',
                   'updated', 'redirect', 'created', 'updated',
                   'feedburner_url', 'keywords')
