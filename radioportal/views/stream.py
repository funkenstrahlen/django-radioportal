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

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from radioportal.models import Stream, Episode
from django.views.generic import base, detail, list


class StreamTemplateView(base.TemplateResponseMixin,
                         base.View, detail.SingleObjectMixin):

    template_name = 'radioportal/stream/playlist.m3u'
    model = Stream
    slug_field = 'mount'
    context_object_name = 'stream'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['streamurl'] = request.build_absolute_uri(self.object.mount)
        response_kwargs = {}
        response_kwargs['mimetype'] = 'audio/x-mpegurl'
        return self.render_to_response(context, **response_kwargs)

class StreamListTemplateView(base.TemplateResponseMixin,
                         base.View, list.MultipleObjectMixin):

    template_name = 'radioportal/stream/playlist_list.m3u'
    queryset = Episode.objects.filter(status="RUNNING")
    context_object_name = 'streams'

    def get(self, request, *args, **kwargs):
        self.object_list = []
        for episode in self.get_queryset():
            self.object_list.extend(episode.channel.running_streams())
        for o in self.object_list:
            o.fullurl = request.build_absolute_uri(o.mount)
        context = self.get_context_data(object_list=self.object_list)
        response_kwargs = {}
        response_kwargs['mimetype'] = 'audio/x-mpegurl'
        return self.render_to_response(context, **response_kwargs)


def stream(request, **kwargs):
        return HttpResponse(_("This URL should be mapped to the backend."))
