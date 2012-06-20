from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.utils.feedgenerator import Atom1Feed, rfc3339_date

from django.db.models.aggregates import Max, Sum, Min

import vobject
import datetime
import pytz

from django_hosts.reverse import reverse_full

from radioportal.models import Show, Episode, Channel
from django.conf import settings

_mapping = {'live': 'RUNNING', 'upcoming': 'UPCOMING', 'recent': 'ARCHIVED'}


class _dummy:
    name = "No title"

    def get_absolute_url(self):
        return "No Link"

    abstract = ""
    description = ""
    isdummy = True

class StreamAtom1Feed(Atom1Feed):
    def root_attributes(self):
        attrs = super(StreamAtom1Feed, self).root_attributes()
        attrs['xmlns:xsn'] = 'http://static.streams.xenim.de/feed-1.0.dtd'
        return attrs

    def add_root_elements(self, handler):
        super(StreamAtom1Feed, self).add_root_elements(handler)
        if 'icon' in self.feed and self.feed['icon']:
            handler.addQuickElement('xsn:icon', self.feed['icon'])

    def add_item_elements(self, handler, item):
        super(StreamAtom1Feed, self).add_item_elements(handler, item)
        handler.addQuickElement('xsn:begin', rfc3339_date(item['begin']))
        if item['end']:
            handler.addQuickElement('xsn:end', rfc3339_date(item['end']))
        if 'icon' in item and item['icon']:
            handler.addQuickElement('xsn:icon', item['icon'])
        if 'streams' in item:
            for stream in item['streams']:
                handler.addQuickElement('xsn:stream', stream)


class ShowFeed(Feed):
    feed_type = StreamAtom1Feed
    def get_object(self, request, show_name=None, status=None):
        if not show_name:
            obj = _dummy()

            def _link():
                return  reverse_full("www", status)

            obj.get_absolute_url = _link
            if status == _mapping.keys()[0]:
                obj.name = _("Running episodes")
                a = _("Currently streamed episodes on xenim streaming network")
                obj.abstract = a
            elif status == _mapping.keys()[1]:
                obj.name = _("Upcoming episodes")
                a = _("Episodes which are scheduled to be aired in the future")
                obj.abstract = a
            elif status == _mapping.keys()[2]:
                obj.name = _("Archived episodes")
                obj.abstract = _("Recently aired episodes")
            return (obj, status)
        return (get_object_or_404(Show, slug=show_name), status)

    def item_extra_kwargs(self, item):
        #print type(item), type(item.begin), type(item.end)
        tz = pytz.timezone(settings.TIME_ZONE)
        begin = item.begin()
        begin = tz.localize(begin)
        end = item.end
        if end:
            end = tz.localize(end)
        extra_dict = {
            'begin': begin,
            'end': end,
        }
        if item.status == "RUNNING":
            try:
                extra_dict['streams'] = []
                for stream in item.channel.stream_set.all():
                    url = reverse_full("www", "mount", view_kwargs={'stream':stream.mount})
                    extra_dict['streams'].append("http:%s" % url)
            except Channel.DoesNotExist:
                pass
        if item.show.icon:
            extra_dict['icon'] = "http:%s" % item.show.icon.url
        return extra_dict

    def feed_extra_kwargs(self, obj):
        extra_dict = {}
        if hasattr(obj[0], 'icon') and obj[0].icon:
            extra_dict['icon'] = "http:%s" % obj[0].icon.url
        return extra_dict

    def item_author_name(self, item):
        return item.show.name

    def item_pubdate(self):
	return datetime.datetime.now()

    def title(self, obj):
        return _("xsn Archive for %s" % obj[0].name)

    def link(self, obj):
        url = obj[0].get_absolute_url()
        return 'http:%s' % url

    def description(self, obj):
        return "%s %s" % (obj[0].abstract, obj[0].description)

    def items(self, obj):
        eps = Episode.objects
        if not hasattr(obj[0], 'isdummy'):
            eps = eps.filter(show=obj[0])
        if obj[1] is not None:
            eps = eps.filter(status=_mapping[obj[1]])
        return eps.annotate(end=Min('parts__end')).order_by('-end')[:30]

    def item_title(self, item):
        return item.title()
        #return unicode(_(u"xsn archive entry %(slug)s: %(title)s")) % {'slug': unicode(item.slug), 'title': unicode(item.title())}

    def item_link(self, item):
        kwargs = {'show_name': item.show.slug, 'slug': item.slug}
        url = reverse_full("www", "episode", view_kwargs=kwargs)
        return 'http:%s' % url

    def item_guid(self, item):
        return unicode("%s-%s") % (item.show.slug, item.slug)

    def item_description(self, item):
        return item.description()

def ical_feed(request, show_name=None):
    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this
    str = ""
    if show_name:
        str= " for %s" % Show.objects.get(slug=show_name).name
    cal.add('X-WR-CALNAME').value = "Upcoming episodes%s on xsn" % str
    cal.add('X-WR-TIMEZONE').value = settings.TIME_ZONE
    ep = Episode.objects.filter(status='UPCOMING')
    if show_name:
        ep = ep.filter(show__slug=show_name)
    for episode in ep.annotate(beginfilter=Min('parts__begin')).order_by('-beginfilter')[:30]:
        vevent = cal.add('vevent')
        val = "%s: %s" % (episode.slug, episode.title())
        vevent.add('summary').value = val
        vevent.add('description').value = episode.description()
        vevent.add('dtstart').value = episode.begin()
        vevent.add('dtend').value = episode.end()
        vevent.add('uid').value = '%s' % episode.pk
        kwargs = {'show_name': episode.show.slug, 'slug': episode.slug}
        url = reverse_full("www", "episode", view_kwargs=kwargs)
        vevent.add('url').value = 'http:%s' % url 
    icalstream = cal.serialize()
    response = HttpResponse(icalstream, mimetype='text/calendar')
    #response['Filename'] = 'filename.ics'  # IE needs this
    #response['Content-Disposition'] = 'attachment; filename=filename.ics'
    return response
