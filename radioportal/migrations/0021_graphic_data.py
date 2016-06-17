# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0020_httpcallbackheader'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphic',
            name='data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
