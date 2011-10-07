'''
Created on 21.05.2011

@author: robert
'''
from django.views.generic.base import TemplateResponseMixin, View
from radioportal.models import Show, Stream, Episode
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models.aggregates import Max, Sum, Min

class RobotsTxtView(TemplateResponseMixin, View):
    
    template_name = "radioportal/robots.txt"
    
    def get(self, request, *args, **kwargs):
        context = {}
        context['shows'] = Show.objects.all()
        context['streams'] = Stream.objects.all()
        request_kwargs = {}
        request_kwargs['mimetype'] = 'text/plain'
        return self.render_to_response(context, **request_kwargs)

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

    def get_queryset(self):
        qs = Episode.objects.all().annotate(begin=Min('parts__begin')).order_by('-begin')
        if 'show_name' in self.kwargs:
            self.allow_empty = False
            if Show.objects.filter(slug=self.kwargs['show_name']).count() == 0:
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
        return context
    
    def get_template_names(self):
        template_name = ""
        if self.what in ("old", "now", "future"):
            template_name = "_%s"% self.what
        return (self.template_base_name % template_name,)


class ShowList(ListView):
    template_name = 'radioportal/episodes/show_list.html'
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
        ctx['archived'] = Episode.objects.filter(status=Episode.STATUS[0][0]).annotate(begin=Min('parts__begin')).order_by('-begin')[:5]
        ctx['upcoming'] = Episode.objects.filter(status=Episode.STATUS[2][0]).annotate(begin=Min('parts__begin')).order_by('begin')[:5]
        return ctx
