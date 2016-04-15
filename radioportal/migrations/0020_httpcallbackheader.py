# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0019_auto_20151227_2107'),
    ]

    operations = [
        migrations.CreateModel(
            name='HTTPCallbackHeader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('value', models.CharField(max_length=250)),
                ('callback', models.ForeignKey(to='radioportal.HTTPCallback')),
            ],
        ),
    ]
