# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Show'
        db.create_table('radioportal_show', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None)),
            ('url', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True)),
            ('twitter', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('chat', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('abstract', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('licence', self.gf('django.db.models.fields.CharField')(default='none', max_length=100, blank=True)),
            ('defaultShortName', self.gf('django.db.models.fields.SlugField')(default='', max_length=50)),
            ('nextEpisodeNumber', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('radioportal', ['Show'])

        # Adding model 'ShowFeed'
        db.create_table('radioportal_showfeed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('show', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['radioportal.Show'], unique=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('feed', self.gf('django.db.models.fields.URLField')(max_length=240, blank=True)),
            ('titlePattern', self.gf('django.db.models.fields.CharField')(max_length=240, blank=True)),
            ('icalfeed', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('radioportal', ['ShowFeed'])

        # Adding model 'Episode'
        db.create_table('radioportal_episode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('show', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radioportal.Show'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(default='', max_length=30)),
            ('status', self.gf('django.db.models.fields.CharField')(default='UPCOMING', max_length=10)),
            ('current_part', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_episode', null=True, to=orm['radioportal.EpisodePart'])),
        ))
        db.send_create_signal('radioportal', ['Episode'])

        # Adding unique constraint on 'Episode', fields ['show', 'slug']
        db.create_unique('radioportal_episode', ['show_id', 'slug'])

        # Adding model 'EpisodePart'
        db.create_table('radioportal_episodepart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('episode', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parts', to=orm['radioportal.Episode'])),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('begin', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('radioportal', ['EpisodePart'])

        # Adding model 'Marker'
        db.create_table('radioportal_marker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('episode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radioportal.EpisodePart'])),
            ('pointoftime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('delete', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('radioportal', ['Marker'])

        # Adding model 'Graphic'
        db.create_table('radioportal_graphic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('episode', self.gf('django.db.models.fields.related.ForeignKey')(related_name='graphics', to=orm['radioportal.EpisodePart'])),
        ))
        db.send_create_signal('radioportal', ['Graphic'])

        # Adding model 'Recording'
        db.create_table('radioportal_recording', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('episode', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recordings', to=orm['radioportal.EpisodePart'])),
            ('path', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('format', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('bitrate', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('publicURL', self.gf('django.db.models.fields.URLField')(default='', max_length=200)),
            ('isPublic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('running', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('radioportal', ['Recording'])

        # Adding model 'Channel'
        db.create_table('radioportal_channel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cluster', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('streamCurrentSong', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('streamGenre', self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True)),
            ('streamShow', self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True)),
            ('streamDescription', self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True)),
            ('streamURL', self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True)),
            ('mapping_method', self.gf('jsonfield.fields.JSONField')()),
            ('currentEpisode', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['radioportal.Episode'], unique=True, null=True, blank=True)),
            ('listener', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('recording', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('agb_accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('agb_accepted_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('graphic_differ_by', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('graphic_title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('radioportal', ['Channel'])

        # Adding M2M table for field show on 'Channel'
        db.create_table('radioportal_channel_show', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('channel', models.ForeignKey(orm['radioportal.channel'], null=False)),
            ('show', models.ForeignKey(orm['radioportal.show'], null=False))
        ))
        db.create_unique('radioportal_channel_show', ['channel_id', 'show_id'])

        # Adding model 'Stream'
        db.create_table('radioportal_stream', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radioportal.Channel'])),
            ('mount', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('running', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('format', self.gf('django.db.models.fields.CharField')(default='mp3', max_length=100)),
            ('bitrate', self.gf('django.db.models.fields.CharField')(default='128', max_length=100)),
            ('encoding', self.gf('django.db.models.fields.CharField')(default='UTF-8', max_length=255)),
            ('fallback', self.gf('django.db.models.fields.CharField')(default='none', max_length=255)),
        ))
        db.send_create_signal('radioportal', ['Stream'])

        # Adding model 'SourcedStream'
        db.create_table('radioportal_sourcedstream', (
            ('stream_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['radioportal.Stream'], unique=True, primary_key=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('radioportal', ['SourcedStream'])

        # Adding model 'RecodedStream'
        db.create_table('radioportal_recodedstream', (
            ('stream_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['radioportal.Stream'], unique=True, primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recoded', to=orm['radioportal.Stream'])),
        ))
        db.send_create_signal('radioportal', ['RecodedStream'])

        # Adding model 'UserProfile'
        db.create_table('radioportal_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('htdigest', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('radioportal', ['UserProfile'])

        # Adding model 'Status'
        db.create_table('radioportal_status', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('verbose_status', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('step', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('radioportal', ['Status'])


    def backwards(self, orm):
        # Removing unique constraint on 'Episode', fields ['show', 'slug']
        db.delete_unique('radioportal_episode', ['show_id', 'slug'])

        # Deleting model 'Show'
        db.delete_table('radioportal_show')

        # Deleting model 'ShowFeed'
        db.delete_table('radioportal_showfeed')

        # Deleting model 'Episode'
        db.delete_table('radioportal_episode')

        # Deleting model 'EpisodePart'
        db.delete_table('radioportal_episodepart')

        # Deleting model 'Marker'
        db.delete_table('radioportal_marker')

        # Deleting model 'Graphic'
        db.delete_table('radioportal_graphic')

        # Deleting model 'Recording'
        db.delete_table('radioportal_recording')

        # Deleting model 'Channel'
        db.delete_table('radioportal_channel')

        # Removing M2M table for field show on 'Channel'
        db.delete_table('radioportal_channel_show')

        # Deleting model 'Stream'
        db.delete_table('radioportal_stream')

        # Deleting model 'SourcedStream'
        db.delete_table('radioportal_sourcedstream')

        # Deleting model 'RecodedStream'
        db.delete_table('radioportal_recodedstream')

        # Deleting model 'UserProfile'
        db.delete_table('radioportal_userprofile')

        # Deleting model 'Status'
        db.delete_table('radioportal_status')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
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
        },
        'radioportal.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'htdigest': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['radioportal']