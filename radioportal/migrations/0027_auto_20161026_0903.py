# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0026_auto_20161025_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='showrequest',
            name='show',
            field=models.ForeignKey(related_name='request', blank=True, to='radioportal.Show', null=True),
        ),
        migrations.AlterField(
            model_name='show',
            name='chat',
            field=models.CharField(default=b'', help_text=b'Location for listeners to chat with eachother. Examples: irc://irc.freenode.net/#xsn, https://slackin.community.metaebene.me/', max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='showrequest',
            name='status',
            field=models.CharField(default=b'NEW', max_length=8, choices=[(b'NEW', 'New'), (b'UNCONFIR', 'Unconfirmed'), (b'ACCEPTED', 'Accepted'), (b'DECLINED', 'Declined')]),
        ),
        migrations.AlterField(
            model_name='showrequest',
            name='user',
            field=models.ForeignKey(related_name='show_requests', to=settings.AUTH_USER_MODEL),
        ),
    ]
