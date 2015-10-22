# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import autoslug.fields
import django.core.files.storage
import podmin.models


class Migration(migrations.Migration):

    dependencies = [
        ('podmin', '0002_make_itunes_cats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='buffer_audio',
            field=models.FileField(upload_to=podmin.models.get_audio_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/var/www/podmin_buffer'), verbose_name=b'audio file'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='buffer_image',
            field=models.ImageField(upload_to=podmin.models.get_image_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/var/www/podmin_buffer'), verbose_name=b'image'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=b'', editable=False, populate_from=b'title', unique=True),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='cleaner',
            field=models.CharField(max_length=255, null=True, verbose_name=b'file cleaner function name', blank=True),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='up_dir',
            field=models.CharField(max_length=255, null=True, verbose_name=b'path to the upload location', blank=True),
        ),
    ]
