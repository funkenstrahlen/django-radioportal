# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('radioportal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EpisodeSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ICalFeed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enabled', models.BooleanField(default=False, verbose_name='Aktivieren')),
                ('icalfeed', models.URLField(max_length=255, verbose_name='iCal feed for upcoming shows', blank=True)),
                ('slug_field', models.CharField(default=b'SUMMARY', max_length=50, choices=[(b'SUMMARY', b'SUMMARY'), (b'DESCRIPTION', b'DESCRIPTION'), (b'LOCATION', b'LOCATION')])),
                ('slug_regex', models.CharField(default=b'(?P<value>{show.defaultShortName}[0-9]+)', max_length=255)),
                ('title_field', models.CharField(default=b'SUMMARY', max_length=50, choices=[(b'SUMMARY', b'SUMMARY'), (b'DESCRIPTION', b'DESCRIPTION'), (b'LOCATION', b'LOCATION')])),
                ('title_regex', models.CharField(default=b'{show.defaultShortName}[0-9]+ (?P<value>.+)', max_length=255)),
                ('description_field', models.CharField(default=b'DESCRIPTION', max_length=50, choices=[(b'SUMMARY', b'SUMMARY'), (b'DESCRIPTION', b'DESCRIPTION'), (b'LOCATION', b'LOCATION')])),
                ('description_regex', models.CharField(default=b'(?P<value>.+)', max_length=255)),
                ('url_field', models.CharField(default=b'LOCATION', max_length=50, choices=[(b'SUMMARY', b'SUMMARY'), (b'DESCRIPTION', b'DESCRIPTION'), (b'LOCATION', b'LOCATION')])),
                ('url_regex', models.CharField(default=b'(?P<value>.+)', max_length=255)),
                ('show', models.OneToOneField(to='radioportal.Show')),
            ],
        ),
        migrations.CreateModel(
            name='ICalEpisodeSource',
            fields=[
                ('episodesource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='radioportal.EpisodeSource')),
                ('identifier', models.CharField(max_length=128)),
                ('source', models.ForeignKey(to='radioportal.ICalFeed')),
            ],
            options={
                'abstract': False,
            },
            bases=('radioportal.episodesource',),
        ),
        migrations.AddField(
            model_name='episodesource',
            name='episode',
            field=models.ForeignKey(related_name='source', to='radioportal.Episode'),
        ),
        migrations.AddField(
            model_name='episodesource',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_radioportal.episodesource_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
