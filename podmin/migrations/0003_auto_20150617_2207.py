# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields
import datetime
import podmin.models


class Migration(migrations.Migration):

    dependencies = [
        ('podmin', '0002_auto_20150128_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='mime_type',
            field=models.CharField(default=b'application/octet-stream', max_length=32, verbose_name=b'audio mime type'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='podcast',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 17, 22, 7, 1, 957813), verbose_name=b'created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='podcast',
            name='image',
            field=sorl.thumbnail.fields.ImageField(upload_to=podmin.models.get_image_upload_path, verbose_name=b'cover art'),
            preserve_default=True,
        ),
    ]
