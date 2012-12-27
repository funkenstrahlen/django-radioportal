# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url, include
from django.views.decorators.cache import cache_page
from django.views.generic import base
from radioportal.views import stream, episodes, graphs


urlpatterns = patterns('',

    url(r'^robots.txt$',
        cache_page(episodes.RobotsTxtView.as_view(), 60 * 60 * 3),
        name="robots"),
        
    #url(r'^dashboard/', include('radioportal.dashboard.urls')),
    
    url(r'^feeds/', include('radioportal.feeds.urls')),
    
    # root
    url(r'^home/$', base.RedirectView.as_view(url='/'), name="home"),
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

    # running streams
    url(r'^live/$', episodes.ShowView.as_view(what='now'), name="live"),
    url(r'^live/(?P<show_name>[\w-]+)/$',
        episodes.ShowView.as_view(what='now'), name="live_show"),

    url(r'^(?P<show_name>[\w-]+)/(?P<slug>[\w-]+)/$',
        episodes.EpisodeView.as_view(), name="episode"),

    url(r'^(?P<show_name>[\w-]+)/$',
        episodes.ShowView.as_view(what="all"), name="show"),

    url(r'^live\.m3u$', stream.StreamListTemplateView.as_view(), name="playlist_list"),

    url(r'^(?P<slug>.*\..{3})\.m3u$',
        cache_page(stream.StreamTemplateView.as_view(), 60 * 60 * 3),
        name="playlist"),
    url(r'^(?P<stream>.*\.(mp3|ogg|ogm|nsv|aac))$',
        stream.stream, name="mount"),

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
