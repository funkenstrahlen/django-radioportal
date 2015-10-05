# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0007_auto_20150717_1905'),
    ]

    operations = [
        migrations.AddField(
            model_name='episodepart',
            name='shownotes_id',
            field=models.CharField(default=b'', max_length=100, verbose_name='ID of this episode on shownot.es', blank=True),
        ),
        migrations.AddField(
            model_name='show',
            name='shownotes_id',
            field=models.CharField(default=b'', max_length=100, verbose_name='ID of this show on shownot.es', blank=True),
        ),
    ]
