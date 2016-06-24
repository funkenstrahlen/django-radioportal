# -*- encoding: utf-8 -*-
# 
# Copyright © 2012 Robert Weidlich. All Rights Reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE LICENSOR "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.
# 
# -*- coding: utf-8 -*-

from radioportal.feeds.feeds import ical_feed, ShowFeed, JsonShowFeed, ShowListFeed, JsonShowListFeed
from radioportal.models import Show
from django.conf.urls import url, patterns, include
from django.views.generic.base import TemplateView

from .api import api_urls

class OverView(TemplateView):
    template_name = 'radioportal/feeds/overview.html'

    def get_context_data(self, **kwargs):
        kwargs['shows'] = Show.objects.all()
        kwargs['p'] = 'upcoming'
        kwargs['l'] = 'live'
        kwargs['la'] = 'recent'
        return kwargs

urlpatterns = patterns('',
    url(r'^$', OverView.as_view()),
    url(r'^api/', include(api_urls)),
    url(r'^upcoming/ical/$', ical_feed, name="upcoming-all-ical"),
    url(r'^feed/$', ShowListFeed(), name="index-feed"),
    url(r'^json/$', JsonShowListFeed(), name="index-json"),
    url(r'^(?P<status>(recent|live|upcoming))/feed/$', ShowFeed(), name="all-feed"),
    url(r'^upcoming/(?P<show_name>[\w-]+)/ical/$', ical_feed, name="upcoming-show-ical"),
    url(r'^(?P<status>(recent|live|upcoming))/(?P<show_name>[\w-]+)/feed/$', ShowFeed(), name="shows-feed"),
    url(r'^(?P<show_name>[\w-]+)/feed/$', ShowFeed(), name="show-feed"),

    url(r'^(?P<status>(recent|live|upcoming))/json/$', JsonShowFeed(), name="all-json"),
    url(r'^(?P<status>(recent|live|upcoming))/(?P<show_name>[\w-]+)/json/$', JsonShowFeed(), name="shows-json"),
    url(r'^(?P<show_name>[\w-]+)/json/$', JsonShowFeed(), name="show-json"),

)
