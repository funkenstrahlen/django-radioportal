# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0002_auto_20150717_1052'),
    ]

    operations = [
        migrations.RenameField(
            model_name='icalfeed',
            old_name='icalfeed',
            new_name='url',
        ),
        migrations.AlterField(
            model_name='episodesource',
            name='episode',
            field=models.OneToOneField(related_name='source', to='radioportal.Episode'),
        ),
    ]
