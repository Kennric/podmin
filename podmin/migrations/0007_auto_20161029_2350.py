# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_markdown.models
import django.core.files.storage
import podmin.models


class Migration(migrations.Migration):

    dependencies = [
        ('podmin', '0006_auto_20151221_2020'),
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
            model_name='episode',
            name='credits',
            field=django_markdown.models.MarkdownField(null=True, verbose_name=b'art and music credits', blank=True),
        ),
        migrations.AlterField(
            model_name='episode',
            name='description',
            field=django_markdown.models.MarkdownField(null=True, verbose_name=b'short episode description', blank=True),
        ),
        migrations.AlterField(
            model_name='episode',
            name='guests',
            field=django_markdown.models.MarkdownField(null=True, verbose_name=b'guests', blank=True),
        ),
        migrations.AlterField(
            model_name='episode',
            name='show_notes',
            field=django_markdown.models.MarkdownField(null=True, verbose_name=b'show notes', blank=True),
        ),
        migrations.AlterField(
            model_name='episode',
            name='summary',
            field=django_markdown.models.MarkdownField(blank=True),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='credits',
            field=django_markdown.models.MarkdownField(null=True, verbose_name=b'art and music credits', blank=True),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='description',
            field=django_markdown.models.MarkdownField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='summary',
            field=django_markdown.models.MarkdownField(blank=True),
        ),
    ]
