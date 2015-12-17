# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0013_auto_20151214_2222'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='public_email',
            field=models.EmailField(default='', max_length=254),
            preserve_default=False,
        ),
    ]
