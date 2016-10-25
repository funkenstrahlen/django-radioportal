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

from django.conf.urls import patterns, url, include
from django.views.decorators.cache import cache_page
from django.views.generic import base
from radioportal.views import stream, episodes, graphs


urlpatterns = patterns('',

    url(r'^robots.txt$',
        cache_page(60 * 60 * 3)(episodes.RobotsTxtView.as_view()),
        name="robots"),
        
    #url(r'^dashboard/', include('radioportal.dashboard.urls')),
    
    url(r'^feeds/', include('radioportal.feeds.urls')),
    
    # root
    url(r'^home/$', base.RedirectView.as_view(url='/', permanent=True), name="home"),
    url(r'^$', episodes.LandingView.as_view(), name="root"),

    #======================================================================
    # # statistic, temp-hack
    # url(r'^statistic/$', list_detail.object_list,
    #    {
    #        'queryset': Channel.objects.select_related().all(),
    #        'template_name': 'portal/statistic.html',
    #    },
    #    name="statistic"
    # ),
    # # Status
    # url(
    #   r'^status/$',
    #   'django.views.generic.list_detail.object_list',
    #   {
    #       'queryset': Status.objects.all().order_by('category'),
    #       'template_name': 'portal/status.html'
    #   },
    #   name="status"
    # ),
    #======================================================================

    url(r'^stats/(?P<slug>[a-z0-9-]+).json', episodes.GraphicStats.as_view(), name="graphic_stats"),

    # archive
    url(r'^shows/$', episodes.ShowList.as_view(), name="shows"),

    # recent
    url(r'^recent/$', episodes.ShowView.as_view(what='old'), name="recent"),
    url(r'^recent/(?P<show_name>[\w-]+)/$',
        episodes.ShowView.as_view(what='old'), name="recent_show"),

    # upcoming
    url(r'^upcoming/$', episodes.ShowView.as_view(what='future'),
        name="upcoming"),
    url(r'^upcoming/(?P<show_name>[\w-]+)/$',
        episodes.ShowView.as_view(what='future'), name="upcoming_show"),

    # embedable

    url(r'^live/(?P<show_name>[\w-]+)/embed/$',
        episodes.EmbedShowView.as_view(what='now'), name="embed_live_show"),
    url(r'^(?P<show_name>[\w-]+)/embed/$',
        episodes.EmbedShowView.as_view(what="all"), name="embed_show"),

    # running streams
    url(r'^live/$', episodes.ShowView.as_view(what='now'), name="live"),
    url(r'^live/(?P<show_name>[\w-]+)/$',
        episodes.ShowView.as_view(what='now'), name="live_show"),

    url(r'^(?P<show_name>[\w-]+)/(?P<slug>[\w-]+)/$',
        episodes.EpisodeView.as_view(), name="episode"),

    url(r'^(?P<show_name>[\w-]+)/$',
        episodes.ShowView.as_view(what="all"), name="show"),

    url(r'^live\.m3u$', stream.StreamListTemplateView.as_view(), name="playlist_list"),

    url(r'^(?P<slug>.*\..{3,4})\.m3u$',
        cache_page(60 * 60 * 3)(stream.StreamTemplateView.as_view()),
        name="playlist"),
    url(r'^(?P<stream>.*\.(mp3|ogg|ogm|nsv|aac|m3u8|opus))$',
        stream.StreamView.as_view(), name="mount"),

    # graphs
    url(r'^graphs/weekday/(?P<show_name>[\w-]+)/$', graphs.weekday_graph,
        name="weekday_graph"),
    url(r'^graphs/hours/(?P<show_name>[\w-]+)/$', graphs.hours_graph,
        name="hours_graph"),
    url(r'^graphs/weekday_hours/(?P<show_name>[\w-]+)/$', graphs.weekday_hours_graph,
        name="weekday_hours_graph"),
    url(r'^graphs/time_per_episode/(?P<show_name>[\w-]+)/$', graphs.time_per_episode_graph,
        name="time_per_episode_graph"),
)
