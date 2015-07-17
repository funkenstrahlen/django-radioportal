# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0003_auto_20150717_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='icalfeed',
            name='filter_field',
            field=models.CharField(default=b'SUMMARY', max_length=50, choices=[(b'SUMMARY', b'SUMMARY'), (b'DESCRIPTION', b'DESCRIPTION'), (b'LOCATION', b'LOCATION')]),
        ),
        migrations.AddField(
            model_name='icalfeed',
            name='filter_regex',
            field=models.CharField(default=b'noshow', max_length=255),
        ),
    ]
