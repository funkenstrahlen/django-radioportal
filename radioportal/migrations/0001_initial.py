# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import jsonfield.fields
import radioportal.models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cluster', models.CharField(help_text='Kennung des Streams (f\xfcr internen Gebrauch)', unique=True, max_length=40)),
                ('streamCurrentSong', models.CharField(default=b'', help_text='Property \xbbcurrent_song\xab from stream meta data', max_length=255, blank=True)),
                ('streamGenre', models.CharField(default=b'', help_text='Property \xbbgenre\xab from stream meta data', max_length=250, blank=True)),
                ('streamShow', models.CharField(default=b'', help_text='Property \xbbshow\xab from stream meta data', max_length=250, blank=True)),
                ('streamDescription', models.CharField(default=b'', help_text='Property \xbbdescription\xab from stream meta data', max_length=250, blank=True)),
                ('streamURL', models.URLField(default=b'', help_text='Property \xbburl\xab from stream meta data', blank=True)),
                ('mapping_method', jsonfield.fields.JSONField(default=dict, help_text='Methoden zur Zuordnung von Stream zu angek\xfcndigten Folgen konfigurieren. Mit der Drop-Down-Box k\xf6nnen Methoden hinzugef\xfcgt werden, mit drag&drop kann die Reihenfolge ver\xe4ndert werden und mit \xd7 k\xf6nnen Methoden wieder aus der Liste entfernt werden.', verbose_name='Algorithmus zur Zuordnung von Folgen zu Streams')),
                ('listener', models.IntegerField(default=0)),
                ('recording', models.BooleanField(default=True, editable=False)),
                ('public_recording', models.BooleanField(default=True, editable=False)),
                ('graphic_differ_by', models.CharField(max_length=255, blank=True)),
                ('graphic_title', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'permissions': (('change_stream', 'Change Stream'),),
            },
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(default=b'', max_length=30, verbose_name='Abgek\xfcrzter Name')),
                ('status', models.CharField(default=b'UPCOMING', max_length=10, choices=[(b'ARCHIVED', 'Archivierte Folge'), (b'RUNNING', 'Laufende Folge'), (b'UPCOMING', 'Geplante Folge')])),
            ],
        ),
        migrations.CreateModel(
            name='EpisodePart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=200, verbose_name='Thema', blank=True)),
                ('description', models.CharField(default=b'', max_length=200, verbose_name='Beschreibung', blank=True)),
                ('begin', models.DateTimeField(verbose_name='Anfang')),
                ('end', models.DateTimeField(null=True, verbose_name='Ende', blank=True)),
                ('url', models.URLField(help_text='Webseite zur Folge', verbose_name='Adresse (URL)', blank=True)),
                ('episode', models.ForeignKey(related_name='parts', to='radioportal.Episode')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Graphic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.ImageField(upload_to=radioportal.models.get_graphic_path, blank=True)),
                ('type', models.CharField(default=b'', max_length=10, choices=[(b'server', 'Listener Statistics Grouped by Server'), (b'mount', 'Listener Statistics Grouped by Mount Point')])),
                ('episode', models.ForeignKey(related_name='graphics', to='radioportal.EpisodePart')),
            ],
        ),
        migrations.CreateModel(
            name='Marker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pointoftime', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255)),
                ('link', models.URLField(blank=True)),
                ('delete', models.BooleanField(default=True)),
                ('episode', models.ForeignKey(to='radioportal.EpisodePart')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('origin', models.CharField(max_length=50)),
                ('message', models.CharField(max_length=255)),
                ('severity', models.PositiveIntegerField(default=3)),
                ('read', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['read', '-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='NotificationPath',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=250, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PrimaryNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('system', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(unique=True, max_length=250)),
                ('format', models.CharField(max_length=50)),
                ('bitrate', models.CharField(max_length=50)),
                ('publicURL', models.URLField(default=b'')),
                ('isPublic', models.BooleanField(default=False)),
                ('size', models.PositiveIntegerField()),
                ('running', models.BooleanField(default=False)),
                ('episode', models.ForeignKey(related_name='recordings', to='radioportal.EpisodePart')),
            ],
        ),
        migrations.CreateModel(
            name='SecondaryNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Show',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='Name der Sendung')),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, populate_from=b'name', editable=False)),
                ('url', models.URLField(default=b'', verbose_name='Webseite der Sendung', blank=True)),
                ('twitter', models.CharField(default=b'', help_text=b'Name of the associated Twitter account', max_length=100, blank=True)),
                ('chat', models.CharField(default=b'', help_text=b'Associated IRC network and channel. Contact administrator for unlisted networks.', max_length=100, blank=True)),
                ('description', models.CharField(default=b'', max_length=200, verbose_name='Beschreibung', blank=True)),
                ('abstract', models.TextField(default=b'', verbose_name='Ausf\xfchrliche Beschreibung', blank=True)),
                ('licence', models.CharField(default=b'none', max_length=100, verbose_name='Lizenz', blank=True, choices=[(b'none', 'none'), (b'cc-by', 'cc-by'), (b'cc-by-sa', 'cc-by-sa'), (b'cc-by-nd', 'cc-by-nd'), (b'cc-by-nc', 'cc-by-nc'), (b'cc-by-nc-sa', 'cc-by-nc-sa'), (b'cc-by-nc-nd', 'cc-by-nc-nd')])),
                ('defaultShortName', models.SlugField(default=b'', help_text='Used to construct the episode identifier.', verbose_name='Abk\xfcrzung des Sendungsnamens')),
                ('nextEpisodeNumber', models.PositiveIntegerField(default=1, help_text='Nummer der n\xe4chsten gesendeten Folge. Wird verwendet, um den Bezeichner einer neuen Folge zu erstellen.', verbose_name='Nummer der n\xe4chsten Folge')),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(upload_to=b'show-icons/', blank=True)),
            ],
            options={
                'permissions': (('change_episodes', 'L\xf6sche Folgen'),),
            },
        ),
        migrations.CreateModel(
            name='ShowFeed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enabled', models.BooleanField(default=False, verbose_name='Aktivieren')),
                ('feed', models.URLField(max_length=240, verbose_name='Feed des Podcasts', blank=True)),
                ('titlePattern', models.CharField(help_text='Wird verwendet, um die ID der Folge und den Titel aus dem Feed zu separieren. Sollte die Gruppen \xbbid\xab und \xbbtitle\xab enthalten.', max_length=240, verbose_name='Regul\xe4rer Ausdruck f\xfcr den Titel', blank=True)),
                ('icalfeed', models.URLField(max_length=255, verbose_name='iCal feed for upcoming shows', blank=True)),
                ('show', models.OneToOneField(to='radioportal.Show')),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('status', models.PositiveSmallIntegerField()),
                ('verbose_status', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField()),
                ('category', models.CharField(max_length=100)),
                ('step', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mount', models.CharField(unique=True, max_length=80)),
                ('running', models.BooleanField(default=False)),
                ('format', models.CharField(default=b'mp3', max_length=100, choices=[(b'mp3', 'MP3'), (b'aac', 'AAC'), (b'ogg', 'Ogg/Vorbis'), (b'ogm', 'Ogg/Theora')])),
                ('bitrate', models.CharField(default=b'128', max_length=100, choices=[(b'32', b'~32 KBit/s'), (b'40', b'~40 KBit/s'), (b'48', b'~48 KBit/s'), (b'56', b'~56 KBit/s'), (b'64', b'~64 KBit/s'), (b'72', b'~72 KBit/s'), (b'80', b'~80 KBit/s'), (b'88', b'~88 KBit/s'), (b'96', b'~96 KBit/s'), (b'104', b'~104 KBit/s'), (b'112', b'~112 KBit/s'), (b'120', b'~120 KBit/s'), (b'128', b'~128 KBit/s'), (b'136', b'~136 KBit/s'), (b'144', b'~144 KBit/s'), (b'152', b'~152 KBit/s'), (b'160', b'~160 KBit/s'), (b'168', b'~168 KBit/s'), (b'176', b'~176 KBit/s'), (b'184', b'~184 KBit/s'), (b'192', b'~192 KBit/s'), (b'200', b'~200 KBit/s'), (b'208', b'~208 KBit/s'), (b'216', b'~216 KBit/s'), (b'224', b'~224 KBit/s'), (b'232', b'~232 KBit/s'), (b'240', b'~240 KBit/s'), (b'248', b'~248 KBit/s'), (b'256', b'~256 KBit/s')])),
                ('encoding', models.CharField(default=b'UTF-8', max_length=255, choices=[(b'UTF-8', 'UTF-8'), (b'ISO8859-15', 'ISO8859-15')])),
                ('fallback', models.CharField(default=b'none', max_length=255, choices=[(b'none', 'No Fallback'), (b'sine', 'Sine'), (b'square', 'Square'), (b'saw', 'Saw'), (b'triangle', 'Triangle'), (b'silence', 'Silence'), (b'white-noise', 'White uniform noise'), (b'pink-noise', 'Pink noise'), (b'sine-table', 'Sine table'), (b'ticks', 'Periodic Ticks'), (b'gaussian-noise', 'White Gaussian noise')])),
            ],
        ),
        migrations.CreateModel(
            name='AuphonicAccount',
            fields=[
                ('notificationpath_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='radioportal.NotificationPath')),
                ('access_token', models.CharField(max_length=250)),
                ('username', models.CharField(max_length=250)),
                ('userid', models.CharField(max_length=250)),
                ('preset', models.CharField(max_length=250, blank=True)),
                ('start_production', models.BooleanField(default=False)),
            ],
            bases=('radioportal.notificationpath',),
        ),
        migrations.CreateModel(
            name='HTTPCallback',
            fields=[
                ('notificationpath_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='radioportal.NotificationPath')),
                ('url', models.URLField()),
            ],
            bases=('radioportal.notificationpath',),
        ),
        migrations.CreateModel(
            name='IRCChannel',
            fields=[
                ('notificationpath_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='radioportal.NotificationPath')),
                ('url', models.CharField(max_length=250)),
            ],
            bases=('radioportal.notificationpath',),
        ),
        migrations.CreateModel(
            name='RecodedStream',
            fields=[
                ('stream_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='radioportal.Stream')),
            ],
            bases=('radioportal.stream',),
        ),
        migrations.CreateModel(
            name='SourcedStream',
            fields=[
                ('stream_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='radioportal.Stream')),
                ('user', models.CharField(default=b'source', max_length=255, blank=True)),
                ('password', models.CharField(max_length=255, blank=True)),
            ],
            bases=('radioportal.stream',),
        ),
        migrations.CreateModel(
            name='TwitterAccount',
            fields=[
                ('notificationpath_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='radioportal.NotificationPath')),
                ('screen_name', models.CharField(max_length=250)),
                ('oauth_token', models.CharField(max_length=250)),
                ('oauth_secret', models.CharField(max_length=250)),
            ],
            bases=('radioportal.notificationpath',),
        ),
        migrations.AddField(
            model_name='stream',
            name='channel',
            field=models.ForeignKey(to='radioportal.Channel'),
        ),
        migrations.AddField(
            model_name='secondarynotification',
            name='path',
            field=models.ForeignKey(to='radioportal.NotificationPath'),
        ),
        migrations.AddField(
            model_name='secondarynotification',
            name='primary',
            field=models.ForeignKey(blank=True, to='radioportal.PrimaryNotification', null=True),
        ),
        migrations.AddField(
            model_name='secondarynotification',
            name='show',
            field=models.ForeignKey(to='radioportal.Show'),
        ),
        migrations.AddField(
            model_name='primarynotification',
            name='path',
            field=models.ForeignKey(to='radioportal.NotificationPath'),
        ),
        migrations.AddField(
            model_name='primarynotification',
            name='rollover',
            field=models.OneToOneField(related_name='rollover', to='radioportal.NotificationTemplate'),
        ),
        migrations.AddField(
            model_name='primarynotification',
            name='show',
            field=models.ForeignKey(to='radioportal.Show'),
        ),
        migrations.AddField(
            model_name='primarynotification',
            name='start',
            field=models.OneToOneField(related_name='start', to='radioportal.NotificationTemplate'),
        ),
        migrations.AddField(
            model_name='primarynotification',
            name='stop',
            field=models.OneToOneField(related_name='stop', to='radioportal.NotificationTemplate'),
        ),
        migrations.AddField(
            model_name='episode',
            name='current_part',
            field=models.ForeignKey(related_name='current_episode', blank=True, to='radioportal.EpisodePart', null=True),
        ),
        migrations.AddField(
            model_name='episode',
            name='show',
            field=models.ForeignKey(verbose_name='Sendung', to='radioportal.Show'),
        ),
        migrations.AddField(
            model_name='channel',
            name='currentEpisode',
            field=models.OneToOneField(null=True, blank=True, to='radioportal.Episode'),
        ),
        migrations.AddField(
            model_name='channel',
            name='show',
            field=models.ManyToManyField(help_text='Sendungen, die diesem Channel zugeordnet sind', to='radioportal.Show', verbose_name='Zugeordnete Sendungen', blank=True),
        ),
        migrations.CreateModel(
            name='HLSStream',
            fields=[
                ('recodedstream_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='radioportal.RecodedStream')),
            ],
            bases=('radioportal.recodedstream',),
        ),
        migrations.AddField(
            model_name='recodedstream',
            name='source',
            field=models.ForeignKey(related_name='recoded', to='radioportal.SourcedStream'),
        ),
        migrations.AlterUniqueTogether(
            name='episode',
            unique_together=set([('show', 'slug')]),
        ),
    ]
