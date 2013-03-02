# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Message'
        db.create_table('radioportal_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('severity', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('radioportal', ['Message'])


    def backwards(self, orm):
        # Deleting model 'Message'
        db.delete_table('radioportal_message')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'radioportal.channel': {
            'Meta': {'object_name': 'Channel'},
            'agb_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'agb_accepted_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cluster': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'currentEpisode': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['radioportal.Episode']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'graphic_differ_by': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'graphic_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listener': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mapping_method': ('jsonfield.fields.JSONField', [], {}),
            'recording': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['radioportal.Show']", 'null': 'True', 'blank': 'True'}),
            'streamCurrentSong': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'streamDescription': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'streamGenre': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'streamShow': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'streamURL': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'radioportal.episode': {
            'Meta': {'unique_together': "(('show', 'slug'),)", 'object_name': 'Episode'},
            'current_part': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_episode'", 'null': 'True', 'to': "orm['radioportal.EpisodePart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radioportal.Show']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '30'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'UPCOMING'", 'max_length': '10'})
        },
        'radioportal.episodepart': {
            'Meta': {'ordering': "['-id']", 'object_name': 'EpisodePart'},
            'begin': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parts'", 'to': "orm['radioportal.Episode']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'radioportal.graphic': {
            'Meta': {'object_name': 'Graphic'},
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'graphics'", 'to': "orm['radioportal.EpisodePart']"}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'radioportal.marker': {
            'Meta': {'object_name': 'Marker'},
            'delete': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radioportal.EpisodePart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pointoftime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'radioportal.message': {
            'Meta': {'object_name': 'Message'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'severity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'radioportal.recodedstream': {
            'Meta': {'object_name': 'RecodedStream', '_ormbases': ['radioportal.Stream']},
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recoded'", 'to': "orm['radioportal.Stream']"}),
            'stream_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['radioportal.Stream']", 'unique': 'True', 'primary_key': 'True'})
        },
        'radioportal.recording': {
            'Meta': {'object_name': 'Recording'},
            'bitrate': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recordings'", 'to': "orm['radioportal.EpisodePart']"}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isPublic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'publicURL': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200'}),
            'running': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'radioportal.show': {
            'Meta': {'object_name': 'Show'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'chat': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'defaultShortName': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'licence': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'nextEpisodeNumber': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None'}),
            'twitter': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'radioportal.showfeed': {
            'Meta': {'object_name': 'ShowFeed'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'feed': ('django.db.models.fields.URLField', [], {'max_length': '240', 'blank': 'True'}),
            'icalfeed': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['radioportal.Show']", 'unique': 'True'}),
            'titlePattern': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'})
        },
        'radioportal.sourcedstream': {
            'Meta': {'object_name': 'SourcedStream', '_ormbases': ['radioportal.Stream']},
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'stream_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['radioportal.Stream']", 'unique': 'True', 'primary_key': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'radioportal.status': {
            'Meta': {'object_name': 'Status'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'step': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'verbose_status': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'radioportal.stream': {
            'Meta': {'object_name': 'Stream'},
            'bitrate': ('django.db.models.fields.CharField', [], {'default': "'128'", 'max_length': '100'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radioportal.Channel']"}),
            'encoding': ('django.db.models.fields.CharField', [], {'default': "'UTF-8'", 'max_length': '255'}),
            'fallback': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'format': ('django.db.models.fields.CharField', [], {'default': "'mp3'", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mount': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'running': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['radioportal']