# -*- coding: utf-8 -*-

from django.views.generic.simple import direct_to_template
from radioportal.feeds.feeds import ical_feed, ShowFeed, JsonShowFeed
from radioportal.models import Show
from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',
    url(r'^$', direct_to_template, 
         {'template': 'radioportal/feeds/overview.html', 
          'extra_context': {'shows': Show.objects.all(), 'p': 'upcoming', 'l': 'live', 'la': 'recent' } }),
    url(r'^upcoming/ical/$', ical_feed, name="upcoming-all-ical"),
    url(r'^(?P<status>(recent|live|upcoming))/feed/$', ShowFeed(), name="all-feed"),
    url(r'^upcoming/(?P<show_name>[\w-]+)/ical/$', ical_feed, name="upcoming-show-ical"),
    url(r'^(?P<status>(recent|live|upcoming))/(?P<show_name>[\w-]+)/feed/$', ShowFeed(), name="shows-feed"),
    url(r'^(?P<show_name>[\w-]+)/feed/$', ShowFeed(), name="show-feed"),

    url(r'^(?P<status>(recent|live|upcoming))/json/$', JsonShowFeed(), name="all-json"),
    url(r'^(?P<status>(recent|live|upcoming))/(?P<show_name>[\w-]+)/json/$', JsonShowFeed(), name="shows-json"),
    url(r'^(?P<show_name>[\w-]+)/json/$', JsonShowFeed(), name="show-json"),

)
