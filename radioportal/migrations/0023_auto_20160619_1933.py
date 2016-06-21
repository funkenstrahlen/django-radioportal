# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0022_graphic_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='icon_etag',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='show',
            name='icon_url',
            field=models.URLField(max_length=255, blank=True),
        ),
    ]
