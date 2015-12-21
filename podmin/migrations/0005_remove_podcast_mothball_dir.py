# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podmin', '0004_auto_20151031_1959'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podcast',
            name='mothball_dir',
        ),
    ]
