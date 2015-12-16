# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0012_auto_20151116_2110'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddField(
            model_name='show',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='stream',
            name='container',
            field=models.CharField(default=b'none', max_length=100, choices=[(b'none', '-'), (b'ogg', 'Ogg'), (b'mpegts', 'MPEG/TS')]),
        ),
    ]
