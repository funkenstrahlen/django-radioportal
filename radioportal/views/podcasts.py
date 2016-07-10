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


class podcast_list(ListView):
    template_name = 'radioportal/podcasts/podcast_list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = Show.objects.all()
        qs = qs.annotate(sum=Sum('episode__id')).filter(sum__gt=0)
        qs = qs.annotate(newest=Max('episode__parts__end')).order_by('-newest')
        return qs

class podcast_detail(ListView):
    template_name = 'radioportal/podcasts/podcast_detail.html'
    
    def get_queryset(self):
        #queryset = Show.objects.all() #annotate(newest=Max('episode__end')).order_by('-newest'),
        qs = Show.objects.all()
        qs = qs.annotate(sum=Sum('episode__id')).filter(sum__gt=0)
        qs = qs.annotate(newest=Max('episode__parts__end')).order_by('-newest')
        return qs
