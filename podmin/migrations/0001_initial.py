# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import autoslug.fields
from django.conf import settings
import django.core.files.storage
import podmin.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('itunes', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255)),
                ('parent', models.ForeignKey(blank=True, to='podmin.Category', null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name=b'updated')),
                ('published', models.DateTimeField(null=True, verbose_name=b'date published')),
                ('title', models.CharField(max_length=255)),
                ('subtitle', models.CharField(max_length=255, null=True, blank=True)),
                ('slug', autoslug.fields.AutoSlugField(default=b'', unique=True, editable=False)),
                ('track_number', models.IntegerField(null=True, verbose_name=b'real episode number', blank=True)),
                ('number', models.CharField(max_length=32, null=True, verbose_name=b'notional episode number', blank=True)),
                ('description', models.TextField(null=True, verbose_name=b'short episode description', blank=True)),
                ('buffer_audio', models.FileField(upload_to=podmin.models.get_audio_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/var/www/podcast_buffer'), verbose_name=b'audio file')),
                ('audio', models.FileField(upload_to=b'', verbose_name=b'audio file')),
                ('guid', models.CharField(unique=True, max_length=255, verbose_name=b'published RSS GUID field')),
                ('part', models.IntegerField(null=True, verbose_name=b'part number of a multipart cast', blank=True)),
                ('pub_date', models.DateTimeField(null=True, verbose_name=b'rss pubdate', blank=True)),
                ('size', models.IntegerField(null=True, verbose_name=b'size in bytes', blank=True)),
                ('length', models.CharField(max_length=32, null=True, verbose_name=b'length in h,m,s format', blank=True)),
                ('mime_type', models.CharField(default=b'application/octet-stream', max_length=32, verbose_name=b'audio mime type')),
                ('active', models.BooleanField(default=1, verbose_name=b'active')),
                ('tags', models.CharField(max_length=255, null=True, verbose_name=b'comma separated list of tags', blank=True)),
                ('show_notes', models.TextField(null=True, verbose_name=b'show notes', blank=True)),
                ('guests', models.TextField(null=True, verbose_name=b'guests', blank=True)),
                ('credits', models.TextField(null=True, verbose_name=b'art and music credits', blank=True)),
                ('image', models.ImageField(upload_to=b'', verbose_name=b'episode image')),
                ('buffer_image', models.ImageField(upload_to=podmin.models.get_image_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/var/www/podcast_buffer'), verbose_name=b'image')),
                ('image_type', models.CharField(max_length=16, verbose_name=b'image file type')),
                ('categorization_domain', models.URLField(blank=True)),
                ('summary', models.TextField(blank=True)),
                ('priority', models.DecimalField(null=True, max_digits=2, decimal_places=1, blank=True)),
                ('block', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-pub_date, part'],
                'get_latest_by': 'pub_date',
            },
        ),
        migrations.CreateModel(
            name='Podcast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('credits', models.TextField(null=True, verbose_name=b'art and music credits', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'created')),
                ('published', models.DateTimeField(null=True, verbose_name=b'last published', blank=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name=b'updated')),
                ('website', models.URLField(null=True, verbose_name=b'podcast website', blank=True)),
                ('frequency', models.CharField(default=b'never', max_length=10, blank=True, choices=[(b'always', b'Always'), (b'hourly', b'Hourly'), (b'daily', b'Daily'), (b'weekly', b'Weekly'), (b'monthly', b'Monthly'), (b'yearly', b'Yearly'), (b'never', b'Never')])),
                ('active', models.BooleanField(default=True)),
                ('feed_format', models.CharField(default=b'rss', max_length=16, verbose_name=b'feed format', choices=[(b'atom', b'Atom'), (b'rss', b'RSS')])),
                ('pub_url', models.URLField(default=b'', verbose_name=b'base publication url', blank=True)),
                ('pub_dir', models.CharField(default=b'', max_length=255, verbose_name=b'rss publication path', blank=True)),
                ('storage_dir', models.CharField(default=b'', max_length=255, verbose_name=b'storage base dir', blank=True)),
                ('storage_url', models.URLField(default=b'', verbose_name=b'storage base url', blank=True)),
                ('tmp_dir', models.CharField(default=b'/tmp', max_length=255, verbose_name=b'path to temporary processing location')),
                ('last_import', models.DateTimeField(null=True, verbose_name=b'last import', blank=True)),
                ('combine_segments', models.BooleanField(default=False)),
                ('publish_segments', models.BooleanField(default=False)),
                ('up_dir', models.CharField(max_length=255, verbose_name=b'path to the upload location')),
                ('cleaner', models.CharField(default=b'default', max_length=255, verbose_name=b'file cleaner function name')),
                ('rename_files', models.BooleanField(default=False)),
                ('tag_audio', models.BooleanField(default=True)),
                ('organization', models.CharField(default=b'', max_length=255)),
                ('station', models.CharField(max_length=16, verbose_name=b'broadcasting station name', blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('author', models.CharField(max_length=255, null=True, blank=True)),
                ('contact', models.EmailField(max_length=255, null=True, blank=True)),
                ('image', models.ImageField(upload_to=podmin.models.get_image_upload_path, verbose_name=b'cover art')),
                ('copyright', models.CharField(max_length=255, null=True, blank=True)),
                ('license', models.CharField(blank=True, max_length=255, null=True, verbose_name=b'license', choices=[(b'All rights reserved', b'All rights reserved'), (b'Creative Commons: Attribution (by)', b'Creative Commons: Attribution (by)'), (b'Creative Commons: Attribution-Share Alike (by-sa)', b'Creative Commons: Attribution-Share Alike (by-sa)'), (b'Creative Commons: Attribution-No Derivatives (by-nd)', b'Creative Commons: Attribution-No Derivatives (by-nd)'), (b'Creative Commons: Attribution-Non-Commercial (by-nc)', b'Creative Commons: Attribution-Non-Commercial (by-nc)'), (b'Creative Commons: Attribution-Non-Commercial-Share Alike         (by-nc-sa)', b'Creative Commons: Attribution-Non-Commercial-Share Alike         (by-nc-sa)'), (b'Creative Commons: Attribution-Non-Commercial-No Dreivatives         (by-nc-nd)', b'Creative Commons: Attribution-Non-Commercial-No Dreivatives         (by-nc-nd)'), (b'Public domain', b'Public domain'), (b'Other', b'Other')])),
                ('copyright_url', models.TextField(null=True, verbose_name=b'copyright url', blank=True)),
                ('language', models.CharField(max_length=8, choices=[(b'en', b'English')])),
                ('feedburner_url', models.URLField(verbose_name=b'FeedBurner URL', blank=True)),
                ('ttl', models.IntegerField(default=1440, verbose_name=b'minutes this feed can be cached')),
                ('tags', models.CharField(max_length=255, null=True, verbose_name=b'comma separated list of tags', blank=True)),
                ('max_age', models.IntegerField(default=365, verbose_name=b'days to keep an episode')),
                ('editor_email', models.EmailField(max_length=254, verbose_name=b'editor email', blank=True)),
                ('webmaster_email', models.EmailField(max_length=254, verbose_name=b'webmaster email', blank=True)),
                ('categorization_domain', models.URLField(blank=True)),
                ('subtitle', models.CharField(max_length=255, blank=True)),
                ('summary', models.TextField(blank=True)),
                ('explicit', models.CharField(default=b'No', max_length=255, blank=True, choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Clean', b'Clean')])),
                ('block', models.BooleanField(default=False)),
                ('redirect', models.URLField(blank=True)),
                ('keywords', models.CharField(max_length=255, blank=True)),
                ('itunes_url', models.URLField(verbose_name=b'iTunes Store URL', blank=True)),
                ('file_rename_format', models.CharField(default=b'{podcast}_{number:0>2}_{date}', max_length=32, verbose_name=b'file name pattern')),
                ('itunes_categories', models.ManyToManyField(to='podmin.Category', blank=True)),
                ('owner', models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='episode',
            name='podcast',
            field=models.ForeignKey(to='podmin.Podcast'),
        ),
        migrations.AlterUniqueTogether(
            name='episode',
            unique_together=set([('podcast', 'track_number'), ('podcast', 'number')]),
        ),
        migrations.AlterOrderWithRespectTo(
            name='episode',
            order_with_respect_to='podcast',
        ),
        migrations.AlterOrderWithRespectTo(
            name='category',
            order_with_respect_to='parent',
        ),
    ]
