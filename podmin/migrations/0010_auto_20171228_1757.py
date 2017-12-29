# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import podmin.models


class Migration(migrations.Migration):

    dependencies = [
        ('podmin', '0009_auto_20171227_2257'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcast',
            name='buffer_dir',
            field=models.CharField(default=b'', max_length=255, verbose_name=b'buffer base dir', blank=True),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='image',
            field=models.ImageField(default=b'./static/img/default_podcast.png', upload_to=podmin.models.get_image_upload_path, verbose_name=b'cover art'),
        ),
    ]
