# -*- coding: utf-8 -*-

from django.views.generic.simple import direct_to_template
from radioportal.feeds.feeds import ical_feed, ShowFeed
from radioportal.models import Show
from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',
    url(r'^$', direct_to_template, 
         {'template': 'portal/feeds/overview.html', 
          'extra_context': {'shows': Show.objects.all(), 'p': 'planned', 'l': 'live', 'la': 'latest' } }),
    url(r'^planned/ical/$', ical_feed, name="planned-all-ical"),
    url(r'^(?P<status>(latest|live|planned))/feed/$', ShowFeed(), name="all-feed"),
    url(r'^planned/(?P<show_name>[\w-]+)/ical/$', ical_feed, name="planned-show-ical"),
    url(r'^(?P<status>(latest|live|planned))/(?P<show_name>[\w-]+)/feed/$', ShowFeed(), name="show-feed"),
    url(r'^(?P<show_name>[\w-]+)/feed/$', ShowFeed(), name="show-feed"),
)
