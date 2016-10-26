# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('radioportal', '0023_auto_20160619_1933'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShowRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('status', models.CharField(default=b'NEW', max_length=8, editable=False, choices=[(b'NEW', 'New'), (b'ACCEPTED', 'Accepted'), (b'DECLINED', 'Declined')])),
                ('feed', models.URLField(blank=True)),
                ('ical', models.URLField(blank=True)),
                ('create_time', models.DateTimeField(editable=False)),
                ('review_time', models.DateTimeField(editable=False)),
                ('review_note', models.CharField(default=b'', max_length=400)),
                ('reviewer', models.ForeignKey(related_name='reviews', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='show_requests', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
