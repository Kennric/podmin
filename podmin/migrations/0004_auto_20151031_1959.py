# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.files.storage
import podmin.models


class Migration(migrations.Migration):

    dependencies = [
        ('podmin', '0003_auto_20151011_0203'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='mothballed',
            field=models.DateTimeField(null=True, verbose_name=b'date mothballed'),
        ),
        migrations.AddField(
            model_name='podcast',
            name='mothball_dir',
            field=models.CharField(default=b'', max_length=255, verbose_name=b'path to archive location'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='buffer_audio',
            field=models.FileField(upload_to=podmin.models.get_audio_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/var/www/staging/podmin_buffer'), verbose_name=b'audio file'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='buffer_image',
            field=models.ImageField(upload_to=podmin.models.get_image_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/var/www/staging/podmin_buffer'), verbose_name=b'image'),
        ),
    ]
