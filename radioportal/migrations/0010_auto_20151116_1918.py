# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0009_auto_20151021_0737'),
    ]

    operations = [
        migrations.AddField(
            model_name='stream',
            name='codec',
            field=models.CharField(default='', max_length=100, choices=[(b'mp3', 'MP3'), (b'aac', 'AAC'), (b'vorbis', 'Vorbis'), (b'theora', 'Theora'), (b'opus', 'Opus')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stream',
            name='container',
            field=models.CharField(default='', max_length=100, choices=[(b'mp3', 'MP3'), (b'ogg', 'OGG'), (b'mpegts', 'MPEG/TS')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stream',
            name='transports',
            field=models.CharField(default='', max_length=100, choices=[(b'http', 'HTTP (Icecast)'), (b'hls', 'Apple HTTP Live Streaming')]),
            preserve_default=False,
        ),
    ]
