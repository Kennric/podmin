# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.files.storage
import podmin.models


class Migration(migrations.Migration):

    dependencies = [
        ('podmin', '0007_auto_20161029_2350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='buffer_audio',
            field=models.FileField(upload_to=podmin.models.get_audio_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/podmin/podmedia//buffer/'), verbose_name=b'audio file'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='buffer_image',
            field=models.ImageField(upload_to=podmin.models.get_image_upload_path, storage=django.core.files.storage.FileSystemStorage(location=b'/podmin/podmedia//buffer/'), verbose_name=b'image'),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='max_age',
            field=models.IntegerField(default=0, verbose_name=b'days to keep an episode'),
        ),
    ]
