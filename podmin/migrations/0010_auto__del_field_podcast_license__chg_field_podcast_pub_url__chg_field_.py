# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Podcast.license'
        db.delete_column(u'podmin_podcast', 'license')


        # Changing field 'Podcast.pub_url'
        db.alter_column(u'podmin_podcast', 'pub_url', self.gf('django.db.models.fields.URLField')(max_length=200))

        # Changing field 'Podcast.storage_url'
        db.alter_column(u'podmin_podcast', 'storage_url', self.gf('django.db.models.fields.URLField')(max_length=200))

    def backwards(self, orm):
        # Adding field 'Podcast.license'
        db.add_column(u'podmin_podcast', 'license',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


        # Changing field 'Podcast.pub_url'
        db.alter_column(u'podmin_podcast', 'pub_url', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Podcast.storage_url'
        db.alter_column(u'podmin_podcast', 'storage_url', self.gf('django.db.models.fields.CharField')(max_length=255))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'podmin.episode': {
            'Meta': {'ordering': "(u'_order',)", 'object_name': 'Episode'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'block': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 20, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'enclosure_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'itunes_categories': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'length': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'part': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'podcast': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['podmin.Podcast']"}),
            'priority': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '2', 'decimal_places': '1', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'show_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'default': "''", 'unique': 'True', 'max_length': '50', 'populate_from': "'title'", 'unique_with': '()'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 20, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        },
        u'podmin.podcast': {
            'Meta': {'object_name': 'Podcast'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'block': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cleaner': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '255'}),
            'combine_segments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'copyright': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'copyright_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 20, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'credits': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'editor_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'explicit': ('django.db.models.fields.CharField', [], {'default': "'No'", 'max_length': '255', 'blank': 'True'}),
            'feedburner': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'default': "'never'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'itunes': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'itunes_categories': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'last_import': ('django.db.models.fields.IntegerField', [], {'default': '1000000000'}),
            'max_age': ('django.db.models.fields.IntegerField', [], {'default': '365'}),
            'organization': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['auth.User']"}),
            'pub_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pub_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'publish_segments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'redirect': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'rename_files': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'title'", 'unique_with': '()'}),
            'station': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'storage_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'storage_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tmp_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': '1440'}),
            'up_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'webmaster_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['podmin']