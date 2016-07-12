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
'''
Created on 21.05.2011

@author: robert
'''

import datetime

from radioportal.models import Show, Stream, Episode, Graphic

from django.db.models.aggregates import Max, Sum, Min
from django.http import JsonResponse
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import DetailView, BaseDetailView
from django.views.generic.list import ListView
from django_hosts.resolvers import reverse

class RobotsTxtView(TemplateResponseMixin, View):
    
    template_name = "radioportal/robots.txt"
    content_type = "text/plain"
    
    def get(self, request, *args, **kwargs):
        context = {}
        context['shows'] = Show.objects.all()
        context['streams'] = Stream.objects.all()
        request_kwargs = {}
        return self.render_to_response(context, **request_kwargs)


class GraphicStats(BaseDetailView):
    model = Graphic
    slug_field = 'uuid'

    def render_to_response(self, context, **kwargs):
        return JsonResponse(self.object.data, safe=False, **kwargs)

class EpisodeView(DetailView):
    model = Episode
    slug_field = 'slug'
    context_object_name = 'episode'
    template_name = 'radioportal/episodes/episode_detail.html'
    
    def get_context_data(self, **kwargs):
       context = super(EpisodeView, self).get_context_data(**kwargs)
       context["show"] = self.object.show
       return context

class EpisodeViewJSON(BaseDetailView):
    model = Episode

    def render_to_response(self, context, **kwargs):
        episode = self.object
        playerConfiguration = {
          "options": {
            "theme": "default"
          },
          "extensions": {
            "EpisodeInfo": {},
            "Playlist": {
              "disabled": "true"
            }
          },
          "podcast": {
            "feed": "%s" % episode.show.podcastfeed.feed_url
          },
          "episode": {
            "media": {
              "mp3": "https://detektor.fm/stream/mp3/musik/"
            },
            "coverUrl": "https://cdn.podigee.com/ppp/samples/cover.jpg",
            "title": "%s" % episode.show.name,
            "subtitle": "%s" % episode.title(),
            "url": "http:%s" % reverse("show_detail", kwargs={'slug': episode.show.slug}, host='www'),
            "embedCode": "<script class=\"podigee-podcast-player\" src=\"https://cdn.podigee.com/podcast-player/javascripts/podigee-podcast-player.js\" data-configuration=\"https:%s\"><\/script>" % reverse("episode_json", kwargs={'slug': episode.slug, 'show_name':episode.show.slug }, host='www'),
            "description": "%s" % episode.show.abstract
          }
        }

        # there is only a channel linked to this episode if it is running
        if episode.status == "RUNNING":
          # iterate over all available streams and add them to the json
          for stream in episode.channel.running_streams:
            url = reverse("mount", kwargs={'stream': stream.mount}, host='www')
            playerConfiguration["episode"]["media"]["%s" % stream.format] = "%s" % url

        response = JsonResponse(playerConfiguration, safe=False, **kwargs)
        # json needs to be accessible from external sources as the player is embeddable
        response["Access-Control-Allow-Origin"] = "*"
        return response

class Calendar(ListView):
    template_name = "radioportal/episodes/calendar.html"
    queryset = Episode.objects.filter(status=Episode.STATUS[1][0]).annotate(begin=Min('parts__begin')).order_by('-begin')
    context_object_name = 'running'
    
    def get_context_data(self, **kwargs):
        ctx = super(Calendar, self).get_context_data(**kwargs)
        ctx['upcoming'] = Episode.objects.filter(status=Episode.STATUS[2][0]).annotate(begin=Min('parts__begin')).filter(begin__gt=datetime.datetime.now()-datetime.timedelta(hours=24)).order_by('begin')
        return ctx
