# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0011_auto_20151116_1920'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stream',
            old_name='transports',
            new_name='transport',
        ),
    ]
