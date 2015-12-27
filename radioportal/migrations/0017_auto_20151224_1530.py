# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0016_auto_20151217_1519'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ShowFeed', 
            new_name='PodcastFeed'
        ),
        migrations.RenameField(
            model_name='PodcastFeed',
            old_name='feed',
            new_name='url'
        ),
        migrations.RemoveField(
            model_name='podcastfeed',
            name='icalfeed',
        ),
    ]
