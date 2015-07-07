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
Created on 09.08.2011

@author: robert
'''

from django.utils.translation import ugettext as _
from django.db.models import Min

import logging
logger = logging.getLogger(__name__)
import re
import inspect
import sys
import datetime

from radioportal.models import Episode, Show


class EpisodeFinder(object):
    def get_name(self):
        return "nothing"

    def get_description(self):
        return _("Does nothing.")

    def get_episode(self, channel, metadata):
        return None


class LatestPlannedEpisode(EpisodeFinder):
    def get_name(self):
        return "find-latest-planned"

    def get_description(self):
        return _("Try to find the earliest possible, existing, upcoming episode")

    def get_episode(self, channel, metadata):
        episode = Episode.objects.filter(
            show__in=channel.show.all(),
            status='UPCOMING').annotate(
                begin=Min('parts__begin')).order_by('begin')[0]
        return episode


class MakeEpisodeMixin(object):
    def _make_episode(self, show, number):
        episode_slug = "%s%03i" % (show.defaultShortName,
                                   number)
        return self._make_episode_slug(show, episode_slug)

    def _make_episode_slug(self, show, slug):
        if slug == "":
            raise Exception()
        episode = Episode(show=show, slug=slug, status=Episode.STATUS[1][0])
        try:
            episode.save()
        except:
            from django.db import connection
            connection._rollback()
            raise
        return episode


class IdExtractor(object):
    """ Abstract base class for extracting the id from the title """
    def get_id(self, title):
        pass


class FirstWordIdExtractor(IdExtractor):
    """ use the first word in the title to get the id """
    def get_id(self, title):
        episode_slug = title.split(" ")[0]
        episode_slug = re.sub(r'[^a-zA-Z0-9]+', '', episode_slug)
        return episode_slug


class FullTitleIdExtractor(IdExtractor):
    """ use the full title as id """
    def get_id(self, title):
        episode_slug = title
        episode_slug = re.sub(r'[^a-zA-Z0-9]+', '', episode_slug)
        return episode_slug


class EpisodeSlugFromTitle(FirstWordIdExtractor, EpisodeFinder):
    def get_name(self):
        return "find-from-title"

    def get_description(self):
        return _("Try to find an existing episode with a slug,"
                 " which is the same as the first word of the stream name")

    def get_episode(self, channel, metadata):
        episode_slug = self.get_id(metadata['name'])
        print "episode_slug: ", episode_slug
        try:
            episode = Episode.objects.get(
                show__in=channel.show.all(),
                slug__iexact=episode_slug)
            return episode
        except Episode.MultipleObjectsReturned:
            logger.error("more than one episode found")
        except Episode.DoesNotExist:
            pass


class MakeEpisodeFromNumberInShow(EpisodeFinder, MakeEpisodeMixin):
    def get_name(self):
        return "make-from-number-in-show"

    def get_description(self):
        return _("Create a new episode using the episodeNumber stored in the show")

    def get_episode(self, channel, metadata):
        for show in channel.show.all():
            show.nextEpisodeNumber += 1
            show.save()
            return self._make_episode(show, show.nextEpisodeNumber)


class MakeEpisodeFromLastEpisode(EpisodeFinder, MakeEpisodeMixin):
    def get_name(self):
        return "make-from-number-of-last-episode"

    def get_description(self):
        return _("Create a new episode by incrementing the number of"
                 " the last episode by one")

    def get_episode(self, channel, metadata):
        last_episode = Episode.objects.filter(
            show__in=channel.show.all(),
            status='ARCHIVED').annotate(
                begin=Min('parts__begin')).order_by('-begin')[0]
        id_str = re.sub(r'[^0-9]+', '', last_episode.slug)
        if id_str == '':
            id_str = '0'
        id = int(id_str) + 1
        return self._make_episode(last_episode.show, id)


class ShowFinder(object):
    def get_show(self, channel, slug): 
        showslug = re.sub(r'[^a-zA-Z]+', '', slug)
        print "showslug: ", showslug
        return channel.show.get(defaultShortName__iexact=showslug)


class FallbackShowFinder(ShowFinder):
    def get_show(self, channel, slug):
        show = None
        try:
            show = super(FallbackShowFinder, self).get_show(channel, slug)
        except Show.DoesNotExist:
            show = channel.show.all()[0]
        return show

class MakeEpisodeFromTitle(MakeEpisodeMixin, FallbackShowFinder):
    def get_name(self):
        return "make-from-title"

    def get_description(self):
        return _("Create new episode using the first word of the title as episode id")

    def get_episode(self, channel, metadata):
        slug = self.get_id(metadata["name"])
        print "Got Slug: ", slug
        show = self.get_show(channel, slug)
        print "Found Show: ", show
        return self._make_episode_slug(show, slug)


class MakeEpisodeFromFirstWordTitle(MakeEpisodeFromTitle, FirstWordIdExtractor, EpisodeFinder):
    pass


class MakeEpisodeFromFullTitle(MakeEpisodeFromTitle, FullTitleIdExtractor, EpisodeFinder):
    def get_name(self):
        return "make-from-full-title"

    def get_description(self):
        return _("Create new episode using the full title as ID")


class MakeLiveEpisode(EpisodeFinder, MakeEpisodeMixin):
    def get_name(self):
        return "make-live"

    def get_description(self):
        return _("Create an episode named live with current date suffix")

    def get_episode(self, channel, metadata):
        for show in channel.show.all():
            name = "live%s" % datetime.datetime.now().strftime("%Y%m%d%H%M")
            live = self._make_episode_slug(show, name)
            return live


class FindLiveEpisode(EpisodeFinder, MakeEpisodeMixin):
    name = "live"

    def get_name(self):
        return "find-or-make-live"

    def get_description(self):
        return _("Find or create an episode named \"%s\"" % self.name)

    def get_episode(self, channel, metadata):
        for show in channel.show.all():
            try:
                live = Episode.objects.get(show=show, slug=self.name)
            except Episode.DoesNotExist:
                live = self._make_episode_slug(show, self.name)
            return live


def get_episode_finder():
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    finders = {}
    for name, cls in clsmembers:
        if issubclass(cls, EpisodeFinder):
            finders[cls().get_name()] = cls
    return finders


class episode_finder_list:
    def __iter__(self):
        finders = get_episode_finder()
        doc_finders = {}
        for name, cls in finders.iteritems():
            doc_finders[name] = cls().get_description()
        return doc_finders.iteritems()

    def next(self):
        raise StopIteration
