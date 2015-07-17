# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0006_auto_20150717_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='icalfeed',
            name='url_regex',
            field=models.CharField(default=b'(?P<value>http[^ ]+)', max_length=255),
        ),
    ]
