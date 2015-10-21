# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0008_auto_20151003_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episodepart',
            name='shownotes_id',
            field=models.CharField(default=b'', max_length=100, verbose_name='ID dieser Folge auf shownot.es', blank=True),
        ),
        migrations.AlterField(
            model_name='icalfeed',
            name='url',
            field=models.URLField(max_length=255, verbose_name='iCal Feed f\xfcr geplante Folgen', blank=True),
        ),
        migrations.AlterField(
            model_name='show',
            name='shownotes_id',
            field=models.CharField(default=b'', max_length=100, verbose_name='ID dieser Sendung auf shownot.es', blank=True),
        ),
        migrations.AlterField(
            model_name='showfeed',
            name='icalfeed',
            field=models.URLField(max_length=255, verbose_name='iCal Feed f\xfcr geplante Folgen', blank=True),
        ),
    ]
