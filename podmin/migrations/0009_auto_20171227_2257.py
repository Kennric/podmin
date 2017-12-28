# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.files.storage
import podmin.models


class Migration(migrations.Migration):

    dependencies = [
        ('podmin', '0008_auto_20171211_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='buffer_audio',
            field=models.FileField(upload_to=podmin.models.get_audio_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/media/buffer/'), verbose_name=b'audio file'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='buffer_image',
            field=models.ImageField(upload_to=podmin.models.get_image_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/media/buffer/'), verbose_name=b'image'),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='subtitle',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
