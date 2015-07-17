# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0005_icalfeed_delete_missing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='episodesource',
            name='episode',
        ),
        migrations.AddField(
            model_name='episode',
            name='source',
            field=models.OneToOneField(default=2, to='radioportal.EpisodeSource'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='icalfeed',
            name='filter_field',
            field=models.CharField(default=b'DESCRIPTION', max_length=50, choices=[(b'SUMMARY', b'SUMMARY'), (b'DESCRIPTION', b'DESCRIPTION'), (b'LOCATION', b'LOCATION')]),
        ),
        migrations.AlterField(
            model_name='icalfeed',
            name='filter_regex',
            field=models.CharField(default=b'#noshow', max_length=255),
        ),
    ]
