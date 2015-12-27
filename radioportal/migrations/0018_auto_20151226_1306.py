# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('radioportal', '0017_auto_20151224_1530'),
    ]

    operations = [
        migrations.RenameField(
            model_name='podcastfeed',
            old_name='url',
            new_name='feed_url',
        ),
        migrations.RemoveField(
            model_name='podcastfeed',
            name='titlePattern',
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='abstract_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='abstract_regex',
            field=models.CharField(default=b'(?P<value>.*)', max_length=127),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='abstract_xpath',
            field=models.CharField(default=(b'itunes:summary', b'itunes:summary'), max_length=127, choices=[(b'title', b'title'), (b'link', b'link'), (b'description', b'description'), (b'copyright', b'copyright'), (b'image/url', b'image/url'), (b"atom:link[@rel='payment']", b"atom:link[@rel='payment']"), (b'itunes:summary', b'itunes:summary'), (b'itunes:owner/itunes:email', b'itunes:owner/itunes:email'), (b'itunes:image', b'itunes:image'), (b'itunes:subtitle', b'itunes:subtitle')]),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='description_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='description_regex',
            field=models.CharField(default=b'(?P<value>.*)', max_length=127),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='description_xpath',
            field=models.CharField(default=(b'description', b'description'), max_length=127, choices=[(b'title', b'title'), (b'link', b'link'), (b'description', b'description'), (b'copyright', b'copyright'), (b'image/url', b'image/url'), (b"atom:link[@rel='payment']", b"atom:link[@rel='payment']"), (b'itunes:summary', b'itunes:summary'), (b'itunes:owner/itunes:email', b'itunes:owner/itunes:email'), (b'itunes:image', b'itunes:image'), (b'itunes:subtitle', b'itunes:subtitle')]),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='donation_url_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='donation_url_regex',
            field=models.CharField(default=b'(?P<value>.*)', max_length=127),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='donation_url_xpath',
            field=models.CharField(default=(b"atom:link[@rel='payment']", b"atom:link[@rel='payment']"), max_length=127, choices=[(b'title', b'title'), (b'link', b'link'), (b'description', b'description'), (b'copyright', b'copyright'), (b'image/url', b'image/url'), (b"atom:link[@rel='payment']", b"atom:link[@rel='payment']"), (b'itunes:summary', b'itunes:summary'), (b'itunes:owner/itunes:email', b'itunes:owner/itunes:email'), (b'itunes:image', b'itunes:image'), (b'itunes:subtitle', b'itunes:subtitle')]),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='feed_url_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='icon_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='icon_regex',
            field=models.CharField(default=b'(?P<value>.*)', max_length=127),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='icon_xpath',
            field=models.CharField(default=(b'image/url', b'image/url'), max_length=127, choices=[(b'title', b'title'), (b'link', b'link'), (b'description', b'description'), (b'copyright', b'copyright'), (b'image/url', b'image/url'), (b"atom:link[@rel='payment']", b"atom:link[@rel='payment']"), (b'itunes:summary', b'itunes:summary'), (b'itunes:owner/itunes:email', b'itunes:owner/itunes:email'), (b'itunes:image', b'itunes:image'), (b'itunes:subtitle', b'itunes:subtitle')]),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='licence_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='licence_regex',
            field=models.CharField(default=b'(?P<value>.*)', max_length=127),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='licence_xpath',
            field=models.CharField(default=(b'copyright', b'copyright'), max_length=127, choices=[(b'title', b'title'), (b'link', b'link'), (b'description', b'description'), (b'copyright', b'copyright'), (b'image/url', b'image/url'), (b"atom:link[@rel='payment']", b"atom:link[@rel='payment']"), (b'itunes:summary', b'itunes:summary'), (b'itunes:owner/itunes:email', b'itunes:owner/itunes:email'), (b'itunes:image', b'itunes:image'), (b'itunes:subtitle', b'itunes:subtitle')]),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='name_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='name_regex',
            field=models.CharField(default=b'(?P<value>.*)', max_length=127),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='name_xpath',
            field=models.CharField(default=(b'title', b'title'), max_length=127, choices=[(b'title', b'title'), (b'link', b'link'), (b'description', b'description'), (b'copyright', b'copyright'), (b'image/url', b'image/url'), (b"atom:link[@rel='payment']", b"atom:link[@rel='payment']"), (b'itunes:summary', b'itunes:summary'), (b'itunes:owner/itunes:email', b'itunes:owner/itunes:email'), (b'itunes:image', b'itunes:image'), (b'itunes:subtitle', b'itunes:subtitle')]),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='public_email_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='public_email_regex',
            field=models.CharField(default=b'(?P<value>.*)', max_length=127),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='public_email_xpath',
            field=models.CharField(default=(b'itunes:owner/itunes:email', b'itunes:owner/itunes:email'), max_length=127, choices=[(b'title', b'title'), (b'link', b'link'), (b'description', b'description'), (b'copyright', b'copyright'), (b'image/url', b'image/url'), (b"atom:link[@rel='payment']", b"atom:link[@rel='payment']"), (b'itunes:summary', b'itunes:summary'), (b'itunes:owner/itunes:email', b'itunes:owner/itunes:email'), (b'itunes:image', b'itunes:image'), (b'itunes:subtitle', b'itunes:subtitle')]),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='url_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='url_regex',
            field=models.CharField(default=b'(?P<value>.*)', max_length=127),
        ),
        migrations.AddField(
            model_name='podcastfeed',
            name='url_xpath',
            field=models.CharField(default=(b'link', b'link'), max_length=127, choices=[(b'title', b'title'), (b'link', b'link'), (b'description', b'description'), (b'copyright', b'copyright'), (b'image/url', b'image/url'), (b"atom:link[@rel='payment']", b"atom:link[@rel='payment']"), (b'itunes:summary', b'itunes:summary'), (b'itunes:owner/itunes:email', b'itunes:owner/itunes:email'), (b'itunes:image', b'itunes:image'), (b'itunes:subtitle', b'itunes:subtitle')]),
        ),
    ]
