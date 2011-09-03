# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from radioportal.models import Stream
from django.views.generic import base, detail


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


def stream(request, **kwargs):
        return HttpResponse(_("This URL should be mapped to the backend."))
