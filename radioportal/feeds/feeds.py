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
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.utils.feedgenerator import Atom1Feed, rfc3339_date, SyndicationFeed
from django.core.serializers.json import DjangoJSONEncoder

from django.db.models.aggregates import Max, Sum, Min

import vobject
import datetime
import pytz
import json

from django_hosts.resolvers import reverse


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
        if 'begin' in item and item['begin']:
            handler.addQuickElement('xsn:begin', rfc3339_date(item['begin']))
        if 'end' in item and item['end']:
            handler.addQuickElement('xsn:end', rfc3339_date(item['end']))
        if 'icon' in item and item['icon']:
            handler.addQuickElement('xsn:icon', item['icon'])
        if 'channel' in item:
            handler.startElement("xsn:channel", {'id': item['channel']})
            if 'listener' in item:
                handler.addQuickElement('xsn:listener', item['listener'])
            if 'current_song' in item:
                handler.addQuickElement('xsn:current_song', item['current_song'])
            if 'streams' in item:
                for stream in item['streams']:
                    handler.addQuickElement('xsn:stream', stream)
            handler.endElement("xsn:channel")
        if 'website' in item:
            handler.addQuickElement('xsn:website', item['website'])
            


class ShowFeed(Feed):
    feed_type = StreamAtom1Feed
    def get_object(self, request, show_name=None, status=None):
        if not show_name:
            obj = _dummy()

            def _link():
                return  reverse(status, host='www')

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
        if begin:
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
                    if not stream.running:
                        continue
                    url = reverse("mount", kwargs={'stream':stream.mount}, host='www')
                    extra_dict['streams'].append("http:%s" % url)
                extra_dict['listener'] = str(item.channel.listener)
                extra_dict['channel'] = item.channel.cluster
                extra_dict['current_song'] = item.channel.streamCurrentSong
            except Channel.DoesNotExist:
                pass
        if item.show.icon:
            extra_dict['icon'] = "http:%s" % item.show.icon.url
        if item.url:
            extra_dict['website'] = item.url()
        return extra_dict

    def feed_extra_kwargs(self, obj):
        kwargs = super(ShowFeed, self).feed_extra_kwargs(obj)
        if hasattr(obj[0], 'icon') and obj[0].icon:
            kwargs['icon'] = "http:%s" % obj[0].icon.url
        return kwargs

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
        return eps.annotate(end=Max('parts__end')).order_by('-end')[:30]

    def item_title(self, item):
        return item.title()
        #return unicode(_(u"xsn archive entry %(slug)s: %(title)s")) % {'slug': unicode(item.slug), 'title': unicode(item.title())}

    def item_link(self, item):
        kwargs = {'show_name': item.show.slug, 'slug': item.slug}
        url = reverse("episode", kwargs=kwargs, host='www')
        return 'http:%s' % url

    def item_guid(self, item):
        return item.get_id()
 
    def item_description(self, item):
        return item.description()

def ical_feed(request, show_name=None):
    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this
    str = ""
    if show_name:
        show = get_object_or_404(Show, slug=show_name)
        str= " for %s" % show.name
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
        if episode.end():
            vevent.add('dtend').value = episode.end()
        vevent.add('uid').value = '%s' % episode.pk
        kwargs = {'show_name': episode.show.slug, 'slug': episode.slug}
        url = reverse("episode", kwargs=kwargs, host='www')
        vevent.add('url').value = 'http:%s' % url 
    icalstream = cal.serialize()
    response = HttpResponse(icalstream, content_type='text/calendar')
    #response['Filename'] = 'filename.ics'  # IE needs this
    #response['Content-Disposition'] = 'attachment; filename=filename.ics'
    return response

def remove_null(d):
    return dict([(k, v) for k, v in d.iteritems() if v])

class JSONFeed(SyndicationFeed):
    mime_type = "application/json"

    def write(self, outfile, encoding):
        data={}
        data.update(self.feed)
        data = remove_null(data)
        data['items'] = self.items
        for i in range(0, len(data['items'])):
            data['items'][i] = remove_null(data['items'][i])
        json.dump(data, outfile, cls=DjangoJSONEncoder)
        # outfile is a HttpResponse
        if isinstance(outfile, HttpResponse):
            outfile['Access-Control-Allow-Origin'] = '*'


class JsonShowFeed(ShowFeed):
    feed_type = JSONFeed


class ShowListFeed(Feed):
    feed_type = StreamAtom1Feed
    link = "/"

    def items(self):
        return Show.objects.all()

    def item_guid(self, item):
        return unicode(item.slug)

    def item_title(self, item):
        return item.name

    def item_author_name(self, item):
        return item.name

    def item_description(self, item):
        if item.abstract and item.description:
            return "%s %s" % (item.abstract, item.description)
        elif item.abstract:
            return item.abstract
        else:
            return item.description

    def item_extra_kwargs(self, item):
        extra_dict = {}
        if item.icon:
            extra_dict['icon'] = "http:%s" % item.icon.url
        if item.url:
            extra_dict['website'] = item.url
        return extra_dict

class JsonShowListFeed(ShowListFeed):
    feed_type = JSONFeed

