# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0004_auto_20150717_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='icalfeed',
            name='delete_missing',
            field=models.BooleanField(default=True),
        ),
    ]
