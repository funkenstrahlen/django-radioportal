# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0018_auto_20151226_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podcastfeed',
            name='abstract_xpath',
            field=models.CharField(default=b'//channel/itunes:summary/text()', max_length=127, choices=[(b'//channel/title/text()', b'//channel/title/text()'), (b'//channel/link/text()', b'//channel/link/text()'), (b'//channel/description/text()', b'//channel/description/text()'), (b'//channel/copyright/text()', b'//channel/copyright/text()'), (b'//channel/image/url/text()', b'//channel/image/url/text()'), (b"//channel/atom:link[@rel='payment']/@href", b"//channel/atom:link[@rel='payment']/@href"), (b'//channel/itunes:summary/text()', b'//channel/itunes:summary/text()'), (b'//channel/itunes:owner/itunes:email/text()', b'//channel/itunes:owner/itunes:email/text()'), (b'//channel/itunes:image/@href', b'//channel/itunes:image/@href'), (b'//channel/itunes:subtitle/text()', b'//channel/itunes:subtitle/text()')]),
        ),
        migrations.AlterField(
            model_name='podcastfeed',
            name='description_xpath',
            field=models.CharField(default=b'//channel/description/text()', max_length=127, choices=[(b'//channel/title/text()', b'//channel/title/text()'), (b'//channel/link/text()', b'//channel/link/text()'), (b'//channel/description/text()', b'//channel/description/text()'), (b'//channel/copyright/text()', b'//channel/copyright/text()'), (b'//channel/image/url/text()', b'//channel/image/url/text()'), (b"//channel/atom:link[@rel='payment']/@href", b"//channel/atom:link[@rel='payment']/@href"), (b'//channel/itunes:summary/text()', b'//channel/itunes:summary/text()'), (b'//channel/itunes:owner/itunes:email/text()', b'//channel/itunes:owner/itunes:email/text()'), (b'//channel/itunes:image/@href', b'//channel/itunes:image/@href'), (b'//channel/itunes:subtitle/text()', b'//channel/itunes:subtitle/text()')]),
        ),
        migrations.AlterField(
            model_name='podcastfeed',
            name='donation_url_xpath',
            field=models.CharField(default=b"//channel/atom:link[@rel='payment']/@href", max_length=127, choices=[(b'//channel/title/text()', b'//channel/title/text()'), (b'//channel/link/text()', b'//channel/link/text()'), (b'//channel/description/text()', b'//channel/description/text()'), (b'//channel/copyright/text()', b'//channel/copyright/text()'), (b'//channel/image/url/text()', b'//channel/image/url/text()'), (b"//channel/atom:link[@rel='payment']/@href", b"//channel/atom:link[@rel='payment']/@href"), (b'//channel/itunes:summary/text()', b'//channel/itunes:summary/text()'), (b'//channel/itunes:owner/itunes:email/text()', b'//channel/itunes:owner/itunes:email/text()'), (b'//channel/itunes:image/@href', b'//channel/itunes:image/@href'), (b'//channel/itunes:subtitle/text()', b'//channel/itunes:subtitle/text()')]),
        ),
        migrations.AlterField(
            model_name='podcastfeed',
            name='icon_xpath',
            field=models.CharField(default=b'//channel/image/url/text()', max_length=127, choices=[(b'//channel/title/text()', b'//channel/title/text()'), (b'//channel/link/text()', b'//channel/link/text()'), (b'//channel/description/text()', b'//channel/description/text()'), (b'//channel/copyright/text()', b'//channel/copyright/text()'), (b'//channel/image/url/text()', b'//channel/image/url/text()'), (b"//channel/atom:link[@rel='payment']/@href", b"//channel/atom:link[@rel='payment']/@href"), (b'//channel/itunes:summary/text()', b'//channel/itunes:summary/text()'), (b'//channel/itunes:owner/itunes:email/text()', b'//channel/itunes:owner/itunes:email/text()'), (b'//channel/itunes:image/@href', b'//channel/itunes:image/@href'), (b'//channel/itunes:subtitle/text()', b'//channel/itunes:subtitle/text()')]),
        ),
        migrations.AlterField(
            model_name='podcastfeed',
            name='licence_xpath',
            field=models.CharField(default=b'//channel/copyright/text()', max_length=127, choices=[(b'//channel/title/text()', b'//channel/title/text()'), (b'//channel/link/text()', b'//channel/link/text()'), (b'//channel/description/text()', b'//channel/description/text()'), (b'//channel/copyright/text()', b'//channel/copyright/text()'), (b'//channel/image/url/text()', b'//channel/image/url/text()'), (b"//channel/atom:link[@rel='payment']/@href", b"//channel/atom:link[@rel='payment']/@href"), (b'//channel/itunes:summary/text()', b'//channel/itunes:summary/text()'), (b'//channel/itunes:owner/itunes:email/text()', b'//channel/itunes:owner/itunes:email/text()'), (b'//channel/itunes:image/@href', b'//channel/itunes:image/@href'), (b'//channel/itunes:subtitle/text()', b'//channel/itunes:subtitle/text()')]),
        ),
        migrations.AlterField(
            model_name='podcastfeed',
            name='name_xpath',
            field=models.CharField(default=b'//channel/title/text()', max_length=127, choices=[(b'//channel/title/text()', b'//channel/title/text()'), (b'//channel/link/text()', b'//channel/link/text()'), (b'//channel/description/text()', b'//channel/description/text()'), (b'//channel/copyright/text()', b'//channel/copyright/text()'), (b'//channel/image/url/text()', b'//channel/image/url/text()'), (b"//channel/atom:link[@rel='payment']/@href", b"//channel/atom:link[@rel='payment']/@href"), (b'//channel/itunes:summary/text()', b'//channel/itunes:summary/text()'), (b'//channel/itunes:owner/itunes:email/text()', b'//channel/itunes:owner/itunes:email/text()'), (b'//channel/itunes:image/@href', b'//channel/itunes:image/@href'), (b'//channel/itunes:subtitle/text()', b'//channel/itunes:subtitle/text()')]),
        ),
        migrations.AlterField(
            model_name='podcastfeed',
            name='public_email_xpath',
            field=models.CharField(default=b'//channel/itunes:owner/itunes:email/text()', max_length=127, choices=[(b'//channel/title/text()', b'//channel/title/text()'), (b'//channel/link/text()', b'//channel/link/text()'), (b'//channel/description/text()', b'//channel/description/text()'), (b'//channel/copyright/text()', b'//channel/copyright/text()'), (b'//channel/image/url/text()', b'//channel/image/url/text()'), (b"//channel/atom:link[@rel='payment']/@href", b"//channel/atom:link[@rel='payment']/@href"), (b'//channel/itunes:summary/text()', b'//channel/itunes:summary/text()'), (b'//channel/itunes:owner/itunes:email/text()', b'//channel/itunes:owner/itunes:email/text()'), (b'//channel/itunes:image/@href', b'//channel/itunes:image/@href'), (b'//channel/itunes:subtitle/text()', b'//channel/itunes:subtitle/text()')]),
        ),
        migrations.AlterField(
            model_name='podcastfeed',
            name='url_xpath',
            field=models.CharField(default=b'//channel/link/text()', max_length=127, choices=[(b'//channel/title/text()', b'//channel/title/text()'), (b'//channel/link/text()', b'//channel/link/text()'), (b'//channel/description/text()', b'//channel/description/text()'), (b'//channel/copyright/text()', b'//channel/copyright/text()'), (b'//channel/image/url/text()', b'//channel/image/url/text()'), (b"//channel/atom:link[@rel='payment']/@href", b"//channel/atom:link[@rel='payment']/@href"), (b'//channel/itunes:summary/text()', b'//channel/itunes:summary/text()'), (b'//channel/itunes:owner/itunes:email/text()', b'//channel/itunes:owner/itunes:email/text()'), (b'//channel/itunes:image/@href', b'//channel/itunes:image/@href'), (b'//channel/itunes:subtitle/text()', b'//channel/itunes:subtitle/text()')]),
        ),
        migrations.AlterField(
            model_name='show',
            name='donation_url',
            field=models.URLField(default=b'', max_length=512, verbose_name='URL for donations (flattr, paypal.me) for this show', blank=True),
        ),
    ]
