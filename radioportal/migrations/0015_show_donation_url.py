# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0014_show_public_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='donation_url',
            field=models.URLField(default=b'', verbose_name='URL for donations (flattr, paypal.me) for this show', blank=True),
        ),
    ]
