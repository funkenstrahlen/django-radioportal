# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HLSStream'
        db.create_table(u'radioportal_hlsstream', (
            (u'recodedstream_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['radioportal.RecodedStream'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'radioportal', ['HLSStream'])

        # Adding field 'Graphic.type'
        db.add_column(u'radioportal_graphic', 'type',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10),
                      keep_default=False)

        # Deleting field 'Channel.agb_accepted_date'
        db.delete_column(u'radioportal_channel', 'agb_accepted_date')

        # Deleting field 'Channel.agb_accepted'
        db.delete_column(u'radioportal_channel', 'agb_accepted')

        # Adding field 'Channel.public_recording'
        db.add_column(u'radioportal_channel', 'public_recording',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


        # Changing field 'RecodedStream.source'
        db.alter_column(u'radioportal_recodedstream', 'source_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radioportal.SourcedStream']))

    def backwards(self, orm):
        # Deleting model 'HLSStream'
        db.delete_table(u'radioportal_hlsstream')

        # Deleting field 'Graphic.type'
        db.delete_column(u'radioportal_graphic', 'type')

        # Adding field 'Channel.agb_accepted_date'
        db.add_column(u'radioportal_channel', 'agb_accepted_date',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2015, 1, 16, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'Channel.agb_accepted'
        db.add_column(u'radioportal_channel', 'agb_accepted',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'Channel.public_recording'
        db.delete_column(u'radioportal_channel', 'public_recording')


        # Changing field 'RecodedStream.source'
        db.alter_column(u'radioportal_recodedstream', 'source_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radioportal.Stream']))

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'radioportal.channel': {
            'Meta': {'object_name': 'Channel'},
            'cluster': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'currentEpisode': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['radioportal.Episode']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'graphic_differ_by': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'graphic_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listener': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mapping_method': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'public_recording': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'recording': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['radioportal.Show']", 'null': 'True', 'blank': 'True'}),
            'streamCurrentSong': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'streamDescription': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'streamGenre': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'streamShow': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
            'streamURL': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        u'radioportal.episode': {
            'Meta': {'unique_together': "(('show', 'slug'),)", 'object_name': 'Episode'},
            'current_part': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_episode'", 'null': 'True', 'to': u"orm['radioportal.EpisodePart']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['radioportal.Show']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '30'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'UPCOMING'", 'max_length': '10'})
        },
        u'radioportal.episodepart': {
            'Meta': {'ordering': "['-id']", 'object_name': 'EpisodePart'},
            'begin': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parts'", 'to': u"orm['radioportal.Episode']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'radioportal.graphic': {
            'Meta': {'object_name': 'Graphic'},
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'graphics'", 'to': u"orm['radioportal.EpisodePart']"}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'radioportal.hlsstream': {
            'Meta': {'object_name': 'HLSStream', '_ormbases': [u'radioportal.RecodedStream']},
            u'recodedstream_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['radioportal.RecodedStream']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'radioportal.marker': {
            'Meta': {'object_name': 'Marker'},
            'delete': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['radioportal.EpisodePart']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pointoftime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'radioportal.message': {
            'Meta': {'ordering': "['read', '-timestamp']", 'object_name': 'Message'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'severity': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'radioportal.recodedstream': {
            'Meta': {'object_name': 'RecodedStream', '_ormbases': [u'radioportal.Stream']},
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recoded'", 'to': u"orm['radioportal.SourcedStream']"}),
            u'stream_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['radioportal.Stream']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'radioportal.recording': {
            'Meta': {'object_name': 'Recording'},
            'bitrate': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recordings'", 'to': u"orm['radioportal.EpisodePart']"}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isPublic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'publicURL': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200'}),
            'running': ('django.db.models.fields.BooleanField', [], {}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'radioportal.show': {
            'Meta': {'object_name': 'Show'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'chat': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'defaultShortName': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'licence': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'nextEpisodeNumber': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None'}),
            'twitter': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        u'radioportal.showfeed': {
            'Meta': {'object_name': 'ShowFeed'},
            'enabled': ('django.db.models.fields.BooleanField', [], {}),
            'feed': ('django.db.models.fields.URLField', [], {'max_length': '240', 'blank': 'True'}),
            'icalfeed': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['radioportal.Show']", 'unique': 'True'}),
            'titlePattern': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'})
        },
        u'radioportal.sourcedstream': {
            'Meta': {'object_name': 'SourcedStream', '_ormbases': [u'radioportal.Stream']},
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'stream_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['radioportal.Stream']", 'unique': 'True', 'primary_key': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'default': "'source'", 'max_length': '255', 'blank': 'True'})
        },
        u'radioportal.status': {
            'Meta': {'object_name': 'Status'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'step': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'verbose_status': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'radioportal.stream': {
            'Meta': {'object_name': 'Stream'},
            'bitrate': ('django.db.models.fields.CharField', [], {'default': "'128'", 'max_length': '100'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['radioportal.Channel']"}),
            'encoding': ('django.db.models.fields.CharField', [], {'default': "'UTF-8'", 'max_length': '255'}),
            'fallback': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'format': ('django.db.models.fields.CharField', [], {'default': "'mp3'", 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mount': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'running': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['radioportal']