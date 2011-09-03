from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils.translation import ugettext as _


import vobject
from radioportal.models import Show, Episode

_mapping = {'live': 'RUNNING', 'planned': 'PLANNED', 'latest': 'ARCHIVED'}


class _dummy:
    name = "No title"

    def get_absolute_url(self):
        return "No Link"

    abstract = ""
    description = ""
    isdummy = True


class ShowFeed(Feed):
    def get_object(self, request, show_name=None, status=None):
        if not show_name:
            obj = _dummy()

            def _link():
                return "http://streams.xenim.de/%s/" % status

            obj.get_absolute_url = _link
            if status == _mapping.keys()[0]:
                obj.name = _("Running episodes")
                a = _("Currently streamed episodes on xenim streaming network")
                obj.abstract = a
            elif status == _mapping.keys()[1]:
                obj.name = _("Planned episodes")
                a = _("Episodes which are scheduled to be aired in the future")
                obj.abstract = a
            elif status == _mapping.keys()[2]:
                obj.name = _("Archived episodes")
                obj.abstract = _("Recently aired episodes")
            return (obj, status)
        return (get_object_or_404(Show, slugName=show_name), status)

    def title(self, obj):
        return _("xsn Archive for %s" % obj[0].name)

    def link(self, obj):
        return obj[0].get_absolute_url()

    def description(self, obj):
        return "%s %s" % (obj[0].abstract, obj[0].description)

    def items(self, obj):
        eps = Episode.objects
        if not hasattr(obj[0], 'isdummy'):
            eps = eps.filter(show=obj[0])
        if obj[1] is not None:
            eps = eps.filter(status=_mapping[obj[1]])
        return eps.order_by('-end')[:30]

    def item_title(self, item):
        return _("xsn archive entry %s: %s" % (item.shortName, item.topic))


def ical_feed(request, show_name=None):
    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this
    ep = Episode.objects.filter(status='PLANNED')
    if show_name:
        ep.filter(show__slugName=show_name)
    for episode in ep.order_by('begin')[:30]:
        vevent = cal.add('vevent')
        val = "%s: %s" % (episode.shortName, episode.topic)
        vevent.add('summary').value = val
        vevent.add('description').value = episode.description
        vevent.add('dtstart').value = episode.begin
        vevent.add('dtend').value = episode.end
    icalstream = cal.serialize()
    response = HttpResponse(icalstream, mimetype='text/calendar')
    #response['Filename'] = 'filename.ics'  # IE needs this
    #response['Content-Disposition'] = 'attachment; filename=filename.ics'
    return response
