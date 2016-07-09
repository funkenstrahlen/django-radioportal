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

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.object.data, safe=False, **response_kwargs)


class EpisodeView(DetailView):
    model = Episode
    slug_field = 'slug'
    context_object_name = 'episode'
    template_name = 'radioportal/episodes/episode_detail.html'
    
#    def get_context_data(self, **kwargs):
#        context = super(ShowView, self).get_context_data(**kwargs)
#        if 'show_name' in self.kwargs:
#            context['show_name'] = self.kwargs['show_name']
#            context['show'] = Show.objects.get(slug=self.kwargs['show_name'])
#        else:
#            context['show_name'] = False
#        return context

    
    def get_queryset(self):
        return Episode.objects.filter(show__slug=self.kwargs.get('show_name', None))
    
class ShowView(ListView):
    template_base_name = 'radioportal/episodes/episode_list%s.html'
    model = Episode
    paginate_by = 10
    what = "all"
    base = 'radioportal/base.html'

    def get_queryset(self):
        qs = Episode.objects.all().annotate(begin=Min('parts__begin')).order_by('-begin')
        if 'show_name' in self.kwargs:
            if not Show.objects.filter(slug=self.kwargs['show_name']).exists():
                self.allow_empty = False
                return Episode.objects.none()
            qs = qs.filter(show__slug=self.kwargs['show_name'])
        if hasattr(self, 'what'):
            if self.what in ('old'):
                qs = qs.filter(status=Episode.STATUS[0][0])
            if self.what in ('now'):
                qs = qs.filter(status=Episode.STATUS[1][0])
            if self.what in ('future'):
                qs = qs.filter(status=Episode.STATUS[2][0]).annotate(begin=Min('parts__begin')).order_by('begin')
        return qs

    def get_context_data(self, **kwargs):
        context = super(ShowView, self).get_context_data(**kwargs)
        if 'show_name' in self.kwargs:
            context['show_name'] = self.kwargs['show_name']
            context['show'] = Show.objects.filter(slug=self.kwargs['show_name'])
            if len(context['show']) > 0:
                context['show'] = context['show'][0]
        else:
            context['show_name'] = False
        context['base'] = self.base
        return context
    
    def get_template_names(self):
        template_name = ""
        if self.what in ("old", "now", "future"):
            template_name = "_%s"% self.what
        return (self.template_base_name % template_name,)


class EmbedShowView(ShowView):
    base = 'radioportal/embed.html'


class ShowList(ListView):
    template_name = 'radioportal/episodes/archive.html'
    paginate_by = 10

    def get_queryset(self):
        #queryset = Show.objects.all() #annotate(newest=Max('episode__end')).order_by('-newest'),
        qs = Show.objects.all()
        qs = qs.annotate(sum=Sum('episode__id')).filter(sum__gt=0)
        qs = qs.annotate(newest=Max('episode__parts__end')).order_by('-newest')
        return qs


class LandingView(ListView):
    template_name = "radioportal/episodes/landing.html"
    queryset = Episode.objects.filter(status=Episode.STATUS[1][0]).annotate(begin=Min('parts__begin')).order_by('-begin')[:5]
    context_object_name = 'running'
    
    def get_context_data(self, **kwargs):
        ctx = super(LandingView, self).get_context_data(**kwargs)
        ctx['archived'] = Episode.objects.filter(status=Episode.STATUS[0][0]).annotate(end=Max('parts__end')).order_by('-end')[:5]
        ctx['upcoming'] = Episode.objects.filter(status=Episode.STATUS[2][0]).annotate(begin=Min('parts__begin')).filter(begin__gt=datetime.datetime.now()-datetime.timedelta(hours=24)).order_by('begin')[:5]
        return ctx
