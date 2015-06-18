# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
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
            bases=(models.Model,),
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
                ('description', models.TextField(null=True, verbose_name=b'short episode description', blank=True)),
                ('audio', models.FileField(upload_to=podmin.models.get_media_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/var/www/staging/p/'), verbose_name=b'audio file')),
                ('guid', models.CharField(unique=True, max_length=255, verbose_name=b'published RSS GUID field')),
                ('part', models.IntegerField(null=True, verbose_name=b'part number of a multipart cast', blank=True)),
                ('pub_date', models.DateTimeField(null=True, verbose_name=b'rss pubdate', blank=True)),
                ('size', models.IntegerField(null=True, verbose_name=b'size in bytes', blank=True)),
                ('length', models.CharField(max_length=32, null=True, verbose_name=b'length in h,m,s format', blank=True)),
                ('active', models.BooleanField(default=1, verbose_name=b'active')),
                ('tags', models.CharField(max_length=255, null=True, verbose_name=b'comma separated list of tags', blank=True)),
                ('show_notes', models.TextField(null=True, verbose_name=b'show notes', blank=True)),
                ('image', models.ImageField(upload_to=podmin.models.get_image_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/var/www/staging/p/'), verbose_name=b'image')),
                ('categorization_domain', models.URLField(blank=True)),
                ('summary', models.TextField(blank=True)),
                ('priority', models.DecimalField(null=True, max_digits=2, decimal_places=1, blank=True)),
                ('block', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-pub_date, part'],
                'get_latest_by': 'pub_date',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Podcast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', autoslug.fields.AutoSlugField(unique=True, editable=False)),
                ('buffer_dir', models.CharField(default=b'', max_length=255, verbose_name=b'buffer path', blank=True)),
                ('pub_url', models.URLField(default=b'', verbose_name=b'base publication url', blank=True)),
                ('pub_dir', models.CharField(default=b'', max_length=255, verbose_name=b'rss publication path', blank=True)),
                ('storage_dir', models.CharField(default=b'', max_length=255, verbose_name=b'storage base dir', blank=True)),
                ('storage_url', models.URLField(default=b'', verbose_name=b'storage base url', blank=True)),
                ('tmp_dir', models.CharField(default=b'/tmp', max_length=255, verbose_name=b'path to temporary processing location')),
                ('credits', models.TextField(null=True, verbose_name=b'art and music credits', blank=True)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 1, 28, 19, 50, 6, 30803), verbose_name=b'created', auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name=b'updated')),
                ('website', models.URLField(null=True, verbose_name=b'podcast website', blank=True)),
                ('rename_files', models.BooleanField(default=False)),
                ('frequency', models.CharField(default=b'never', max_length=10, blank=True, choices=[(b'always', b'Always'), (b'hourly', b'Hourly'), (b'daily', b'Daily'), (b'weekly', b'Weekly'), (b'monthly', b'Monthly'), (b'yearly', b'Yearly'), (b'never', b'Never')])),
                ('last_import', models.IntegerField(default=1000000000)),
                ('combine_segments', models.BooleanField(default=False)),
                ('publish_segments', models.BooleanField(default=False)),
                ('up_dir', models.CharField(max_length=255, verbose_name=b'path to the upload location')),
                ('cleaner', models.CharField(default=b'default', max_length=255, verbose_name=b'file cleaner function name')),
                ('organization', models.CharField(default=b'', max_length=255)),
                ('station', models.CharField(max_length=16, verbose_name=b'broadcasting station name', blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('author', models.CharField(max_length=255, null=True, blank=True)),
                ('contact', models.EmailField(max_length=255, null=True, blank=True)),
                ('image', models.ImageField(upload_to=podmin.models.get_image_upload_path, verbose_name=b'cover art')),
                ('copyright', models.CharField(blank=True, max_length=255, null=True, verbose_name=b'license', choices=[(b'All rights reserved', b'All rights reserved'), (b'Creative Commons: Attribution (by)', b'Creative Commons: Attribution (by)'), (b'Creative Commons: Attribution-Share Alike (by-sa)', b'Creative Commons: Attribution-Share Alike (by-sa)'), (b'Creative Commons: Attribution-No Derivatives (by-nd)', b'Creative Commons: Attribution-No Derivatives (by-nd)'), (b'Creative Commons: Attribution-Non-Commercial (by-nc)', b'Creative Commons: Attribution-Non-Commercial (by-nc)'), (b'Creative Commons: Attribution-Non-Commercial-Share Alike         (by-nc-sa)', b'Creative Commons: Attribution-Non-Commercial-Share Alike         (by-nc-sa)'), (b'Creative Commons: Attribution-Non-Commercial-No Dreivatives         (by-nc-nd)', b'Creative Commons: Attribution-Non-Commercial-No Dreivatives         (by-nc-nd)'), (b'Public domain', b'Public domain'), (b'Other', b'Other')])),
                ('copyright_url', models.TextField(null=True, verbose_name=b'copyright url', blank=True)),
                ('language', models.CharField(max_length=8)),
                ('feedburner_url', models.URLField(verbose_name=b'FeedBurner URL', blank=True)),
                ('ttl', models.IntegerField(default=1440, verbose_name=b'minutes this feed can be cached')),
                ('tags', models.CharField(max_length=255, null=True, verbose_name=b'comma separated list of tags', blank=True)),
                ('max_age', models.IntegerField(default=365, verbose_name=b'days to keep an episode')),
                ('editor_email', models.EmailField(max_length=75, verbose_name=b'editor email', blank=True)),
                ('webmaster_email', models.EmailField(max_length=75, verbose_name=b'webmaster email', blank=True)),
                ('categorization_domain', models.URLField(blank=True)),
                ('subtitle', models.CharField(max_length=255, blank=True)),
                ('summary', models.TextField(blank=True)),
                ('explicit', models.CharField(default=b'No', max_length=255, blank=True, choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Clean', b'Clean')])),
                ('block', models.BooleanField(default=False)),
                ('redirect', models.URLField(blank=True)),
                ('keywords', models.CharField(max_length=255, blank=True)),
                ('itunes_url', models.URLField(verbose_name=b'iTunes Store URL', blank=True)),
                ('itunes_categories', models.ManyToManyField(to='podmin.Category', blank=True)),
                ('owner', models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='episode',
            name='podcast',
            field=models.ForeignKey(to='podmin.Podcast'),
            preserve_default=True,
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
