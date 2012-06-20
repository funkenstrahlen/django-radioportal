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
