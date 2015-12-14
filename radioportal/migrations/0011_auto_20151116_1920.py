# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards_func(apps, schema_editor):
    Stream = apps.get_model("radioportal", "Stream")
    db_alias = schema_editor.connection.alias
    for s in Stream.objects.all():
        if s.format == "mp3":
            s.codec = "mp3"
            s.container = "mp3"
            s.transports = "http"
        elif s.format == "ogg":
            s.codec = "vorbis"
            s.container = "ogg"
            s.transports = "http"
        elif s.format == "ogm":
            s.codec = "theora"
            s.container = "ogg"
            s.transports = "http"
        elif s.format == "aac":
            s.codec = "aac"
            s.container = "mpegts"
            s.transports = "hls"
        s.save()

class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0010_auto_20151116_1918'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
        migrations.AlterField(
            model_name='stream',
            name='codec',
            field=models.CharField(default=b'mp3', max_length=100, choices=[(b'mp3', 'MP3'), (b'aac', 'AAC'), (b'vorbis', 'Vorbis'), (b'theora', 'Theora'), (b'opus', 'Opus')]),
        ),
        migrations.AlterField(
            model_name='stream',
            name='container',
            field=models.CharField(default=b'mp3', max_length=100, choices=[(b'mp3', 'MP3'), (b'ogg', 'OGG'), (b'mpegts', 'MPEG/TS')]),
        ),
        migrations.AlterField(
            model_name='stream',
            name='transports',
            field=models.CharField(default=b'http', max_length=100, choices=[(b'http', 'HTTP (Icecast)'), (b'hls', 'Apple HTTP Live Streaming')]),
        ),
    ]
