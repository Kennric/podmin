# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podmin', '0005_remove_podcast_mothball_dir'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcast',
            name='editor_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='podcast',
            name='webmaster_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
