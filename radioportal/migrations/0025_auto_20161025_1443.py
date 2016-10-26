# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0024_showrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='showrequest',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='showrequest',
            name='feed',
            field=models.URLField(verbose_name='Feed of the Podcast, used for automatic extraction of master data', blank=True),
        ),
        migrations.AlterField(
            model_name='showrequest',
            name='ical',
            field=models.URLField(verbose_name='HTTP-Adress of ICal File with announcements of live broadcasts', blank=True),
        ),
        migrations.AlterField(
            model_name='showrequest',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Name of the Podcast'),
        ),
        migrations.AlterField(
            model_name='showrequest',
            name='review_note',
            field=models.CharField(default=b'', max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name='showrequest',
            name='review_time',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='showrequest',
            name='reviewer',
            field=models.ForeignKey(related_name='reviews', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='showrequest',
            name='status',
            field=models.CharField(default=b'NEW', max_length=8, choices=[(b'NEW', 'New'), (b'ACCEPTED', 'Accepted'), (b'DECLINED', 'Declined')]),
        ),
    ]
