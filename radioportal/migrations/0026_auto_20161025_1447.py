# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0025_auto_20161025_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='showrequest',
            name='review_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
