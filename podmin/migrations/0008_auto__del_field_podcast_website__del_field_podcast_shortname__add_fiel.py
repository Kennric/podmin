# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Podcast.website'
        db.delete_column(u'podmin_podcast', 'website')

        # Deleting field 'Podcast.shortname'
        db.delete_column(u'podmin_podcast', 'shortname')

        # Adding field 'Podcast.slug'
        db.add_column(u'podmin_podcast', 'slug',
                      self.gf('autoslug.fields.AutoSlugField')(default=None, unique=True, max_length=50, populate_from='title', unique_with=()),
                      keep_default=False)

        # Adding field 'Podcast.created'
        db.add_column(u'podmin_podcast', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0), auto_now_add=True, blank=True),
                      keep_default=False)

        # Adding field 'Podcast.organization'
        db.add_column(u'podmin_podcast', 'organization',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'Podcast.link'
        db.add_column(u'podmin_podcast', 'link',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Podcast.copyright_url'
        db.add_column(u'podmin_podcast', 'copyright_url',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Podcast.domain'
        db.add_column(u'podmin_podcast', 'domain',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Podcast.feedburner'
        db.add_column(u'podmin_podcast', 'feedburner',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Podcast.editor_email'
        db.add_column(u'podmin_podcast', 'editor_email',
                      self.gf('django.db.models.fields.EmailField')(default='', max_length=75, blank=True),
                      keep_default=False)

        # Adding field 'Podcast.webmaster_email'
        db.add_column(u'podmin_podcast', 'webmaster_email',
                      self.gf('django.db.models.fields.EmailField')(default='', max_length=75, blank=True),
                      keep_default=False)

        # Adding field 'Podcast.summary'
        db.add_column(u'podmin_podcast', 'summary',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Podcast.block'
        db.add_column(u'podmin_podcast', 'block',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Podcast.redirect'
        db.add_column(u'podmin_podcast', 'redirect',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Podcast.keywords'
        db.add_column(u'podmin_podcast', 'keywords',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Podcast.itunes'
        db.add_column(u'podmin_podcast', 'itunes',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Podcast.license'
        db.add_column(u'podmin_podcast', 'license',
                      self.gf('licenses.fields.LicenseField')(to=orm['licenses.License'], null=True, blank=True),
                      keep_default=False)


        # Changing field 'Podcast.image'
        db.alter_column(u'podmin_podcast', 'image', self.gf('django.db.models.fields.files.ImageField')(max_length=100))

        # Changing field 'Podcast.subtitle'
        db.alter_column(u'podmin_podcast', 'subtitle', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Podcast.explicit'
        db.alter_column(u'podmin_podcast', 'explicit', self.gf('django.db.models.fields.CharField')(max_length=255))
        # Adding field 'Episode.created'
        db.add_column(u'podmin_episode', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0), auto_now_add=True, blank=True),
                      keep_default=False)

        # Adding field 'Episode.updated'
        db.add_column(u'podmin_episode', 'updated',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0), auto_now=True, blank=True),
                      keep_default=False)

        # Adding field 'Episode.slug'
        db.add_column(u'podmin_episode', 'slug',
                      self.gf('autoslug.fields.AutoSlugField')(default='', unique=True, max_length=50, populate_from='title', unique_with=()),
                      keep_default=False)

        # Adding field 'Episode.image'
        db.add_column(u'podmin_episode', 'image',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'Episode.category'
        db.add_column(u'podmin_episode', 'category',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Episode.domain'
        db.add_column(u'podmin_episode', 'domain',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Episode.frequency'
        db.add_column(u'podmin_episode', 'frequency',
                      self.gf('django.db.models.fields.CharField')(default='never', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'Episode.summary'
        db.add_column(u'podmin_episode', 'summary',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Podcast.website'
        db.add_column(u'podmin_podcast', 'website',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Podcast.shortname'
        db.add_column(u'podmin_podcast', 'shortname',
                      self.gf('autoslug.fields.AutoSlugField')(default=None, max_length=50, unique_with=(), unique=True, populate_from='title'),
                      keep_default=False)

        # Deleting field 'Podcast.slug'
        db.delete_column(u'podmin_podcast', 'slug')

        # Deleting field 'Podcast.created'
        db.delete_column(u'podmin_podcast', 'created')

        # Deleting field 'Podcast.organization'
        db.delete_column(u'podmin_podcast', 'organization')

        # Deleting field 'Podcast.link'
        db.delete_column(u'podmin_podcast', 'link')

        # Deleting field 'Podcast.copyright_url'
        db.delete_column(u'podmin_podcast', 'copyright_url')

        # Deleting field 'Podcast.domain'
        db.delete_column(u'podmin_podcast', 'domain')

        # Deleting field 'Podcast.feedburner'
        db.delete_column(u'podmin_podcast', 'feedburner')

        # Deleting field 'Podcast.editor_email'
        db.delete_column(u'podmin_podcast', 'editor_email')

        # Deleting field 'Podcast.webmaster_email'
        db.delete_column(u'podmin_podcast', 'webmaster_email')

        # Deleting field 'Podcast.summary'
        db.delete_column(u'podmin_podcast', 'summary')

        # Deleting field 'Podcast.block'
        db.delete_column(u'podmin_podcast', 'block')

        # Deleting field 'Podcast.redirect'
        db.delete_column(u'podmin_podcast', 'redirect')

        # Deleting field 'Podcast.keywords'
        db.delete_column(u'podmin_podcast', 'keywords')

        # Deleting field 'Podcast.itunes'
        db.delete_column(u'podmin_podcast', 'itunes')

        # Deleting field 'Podcast.license'
        db.delete_column(u'podmin_podcast', 'license_id')


        # Changing field 'Podcast.image'
        db.alter_column(u'podmin_podcast', 'image', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Podcast.subtitle'
        db.alter_column(u'podmin_podcast', 'subtitle', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Podcast.explicit'
        db.alter_column(u'podmin_podcast', 'explicit', self.gf('django.db.models.fields.BooleanField')())
        # Deleting field 'Episode.created'
        db.delete_column(u'podmin_episode', 'created')

        # Deleting field 'Episode.updated'
        db.delete_column(u'podmin_episode', 'updated')

        # Deleting field 'Episode.slug'
        db.delete_column(u'podmin_episode', 'slug')

        # Deleting field 'Episode.image'
        db.delete_column(u'podmin_episode', 'image')

        # Deleting field 'Episode.category'
        db.delete_column(u'podmin_episode', 'category')

        # Deleting field 'Episode.domain'
        db.delete_column(u'podmin_episode', 'domain')

        # Deleting field 'Episode.frequency'
        db.delete_column(u'podmin_episode', 'frequency')

        # Deleting field 'Episode.summary'
        db.delete_column(u'podmin_episode', 'summary')


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
        u'licenses.license': {
            'Meta': {'ordering': "('name',)", 'object_name': 'License'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'logo': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'licenses'", 'null': 'True', 'to': u"orm['licenses.Organization']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'licenses.organization': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Organization'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'podmin.episode': {
            'Meta': {'ordering': "(u'_order',)", 'object_name': 'Episode'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'frequency': ('django.db.models.fields.CharField', [], {'default': "'never'", 'max_length': '10', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'length': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'part': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'podcast': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['podmin.Podcast']"}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'show_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'default': "''", 'unique': 'True', 'max_length': '50', 'populate_from': "'title'", 'unique_with': '()'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
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
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'credits': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'editor_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'explicit': ('django.db.models.fields.CharField', [], {'default': "'No'", 'max_length': '255', 'blank': 'True'}),
            'feedburner': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'itunes': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'itunes_categories': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'last_import': ('django.db.models.fields.IntegerField', [], {'default': '1000000000'}),
            'license': ('licenses.fields.LicenseField', [], {'to': u"orm['licenses.License']", 'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'max_age': ('django.db.models.fields.IntegerField', [], {'default': '365'}),
            'organization': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['auth.User']"}),
            'pub_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pub_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'publish_segments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'redirect': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'title'", 'unique_with': '()'}),
            'station': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'storage_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'storage_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tmp_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': '1440'}),
            'up_dir': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'webmaster_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'})
        }
    }

    complete_apps = ['podmin']