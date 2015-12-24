# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0015_show_donation_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='show',
            name='public_email',
            field=models.EmailField(default=b'', max_length=254, blank=True),
        ),
    ]
