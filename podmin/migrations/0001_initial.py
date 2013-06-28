# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Podcast'
        db.create_table(u'podmin_podcast', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('shortname', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('station', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('subtitle', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.EmailField')(max_length=255, null=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('image', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('copyright', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('explicit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('itunes_categories', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('tags', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('last_import', self.gf('django.db.models.fields.IntegerField')()),
            ('combine_segments', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('publish_segments', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pub_dir', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('storage_dir', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('storage_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tmp_dir', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('up_dir', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('cleaner', self.gf('django.db.models.fields.CharField')(default='default', max_length=255)),
            ('ttl', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('max_age', self.gf('django.db.models.fields.IntegerField')(default=365)),
        ))
        db.send_create_signal(u'podmin', ['Podcast'])

        # Adding model 'Episode'
        db.create_table(u'podmin_episode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('podcast', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['podmin.Podcast'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('subtitle', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('guid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('part', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('length', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('current', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tags', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'podmin', ['Episode'])


    def backwards(self, orm):
        # Deleting model 'Podcast'
        db.delete_table(u'podmin_podcast')

        # Deleting model 'Episode'
        db.delete_table(u'podmin_episode')


    models = {
        u'podmin.episode': {
            'Meta': {'ordering': "(u'_order',)", 'object_name': 'Episode'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'part': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'podcast': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['podmin.Podcast']"}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'podmin.podcast': {
            'Meta': {'object_name': 'Podcast'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'cleaner': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '255'}),
            'combine_segments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'copyright': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'explicit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'itunes_categories': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'last_import': ('django.db.models.fields.IntegerField', [], {}),
            'max_age': ('django.db.models.fields.IntegerField', [], {'default': '365'}),
            'pub_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pub_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'publish_segments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'station': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'storage_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'storage_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tmp_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'up_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['podmin']