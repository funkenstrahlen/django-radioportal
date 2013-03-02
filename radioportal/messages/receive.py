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

from django.utils import simplejson
from django.utils.datetime_safe import datetime
from django.contrib.contenttypes.models import ContentType

from django.db import connection
from django.conf import settings

import traceback
import logging
logger = logging.getLogger(__name__)

import re
import urlparse
import urllib
import os.path
import urllib2
import easy_thumbnails.files

from radioportal.models import Channel, Episode, EpisodePart, Stream, Graphic, Recording, Show, Message

# from radioportal_auphonic.models import AuphonicSettings

from radioportal.url_normalize import url_normalize

import dateutil.parser

from .send import dto_map
from .episode_finder import get_episode_finder

import reversion

#### Part two: receiving updates ####


def reply(routing_key, data):
    from carrot.connection import DjangoBrokerConnection
    from carrot.messaging import Publisher

    conn = DjangoBrokerConnection()
    publisher = Publisher(connection=conn,
                          exchange="django",
                          routing_key=routing_key,
                          exchange_type="topic",
                          )
    publisher.send(data)
    publisher.close()
    conn.close()


def error_handler(msg, channel):
    logger.error(msg)
    m=Message(message_object=channel, origin="BackendInterpreter", message=msg,
                       severity=3)
    m.save()

class BackendInterpreter(object):
    def __init__(self, reply_callback):
        self.reply = reply_callback

    def message_send(self, data):
        """
            value={
               'channel': 'nsfw',
               'show': 'not-safe-for-work',
               'origin': 'feedupdater',
               'message': 'error parsing feed',
               'severity': '3',
               'stamp': '2013-02-25T20:35:29'
            }
        """
        if "channel" in data:
            obj = Channel.objects.get(cluster=data["channel"])
        else:
            obj = Channel.objects.get(slug=data["show"])
        if "stamp" in data:
            d = dateutil.parser.parse(data['stamp'])
        else:
            d = None
        m=Message(message_object=obj, origin=data["origin"], message=data["message"],
                       severity=data["severity"], timestamp=d)
        m.save()

    def show_startmaster(self, data):
        """
            value={'name': cpwd, 'time': int, 'show' : {'name': 'CR001 Titel der Sendung'}}
            FIXME: need show
        """
        channel = Channel.objects.get(cluster=data['name'])

        available_methods = get_episode_finder()
        episode = None

        for method in channel.mapping_method:
            # print "trying method", method
            if method not in available_methods:
                error_handler("Mapping method %s not found" % method, channel)
                continue
            finder = available_methods[method]()
            try:
                episode = finder.get_episode(channel, data['show'])
            except Exception, e:
                print "method", method, "failed"
                print traceback.format_exc()
                error_handler("Mapping method %s failed: %s" % (method, e), channel)
                connection._rollback()
            if episode:
                break

        if not episode:
            error_handler("No episode found for cluster %s" % data['name'], channel)
            return

        part = None
        if episode.status == Episode.STATUS[2][0]:
            parts = episode.parts.all().reverse()
            if len(parts) > 0:
                part = parts[0]
        if not part:
            part = EpisodePart(episode=episode)

        part.begin = datetime.now()
        part.save()

        episode.status = "RUNNING"
        episode.current_part = part
        episode.save()

        channel.currentEpisode = episode
        channel.save()

    def show_stop(self, data):
        """
            value={'name': cpwd}
        """
        channel = Channel.objects.get(cluster=data['name'])
        if channel.currentEpisode:
            episode = channel.currentEpisode
            part = episode.current_part
            part.end = datetime.now()
            part.save()
            episode.current_part = None
            episode.status = Episode.STATUS[0][0]
            episode.save()
            channel.currentEpisode = None
            channel.save()
        else:
            error_handler("show_stop: no current episode found for cluster %s" %
                         data['name'], channel)
            # FIXME

    def stream_start(self, data):
        """
            value={'name': mount, 'id': id, 'stream': {'mountpoint': 'mount.mp4', 'bitrate': 128, 'type': 'mp3'}}
            FIXME: Stream object
        """

        mp = data['stream']['mountpoint']

        stream = Stream.objects.filter(mount=mp)
        if len(stream) == 1:
            stream = stream[0]
        else:
            channel = Channel.objects.get(cluster=data['name'].split("-")[0])
            stream = Stream(mount=mp, channel=channel)
        stream.running = True
        stream.bitrate = data['stream']['bitrate']
        stream.format = data['stream']['type'].lower()
        stream.save()
        # stream.channel.updateRunning()

    def stream_stop(self, data):
        """
            value={'name': mount}
        """
        mount = data['name'].split("-")

        stream = Stream.objects.filter(channel__cluster=mount[0], format=mount[
                                       2].lower(), bitrate=int(mount[1]))
        if len(stream) == 1:
            stream = stream[0]
            stream.running = False
            stream.save()

    def show_listener(self, data):
        channel = Channel.objects.get(cluster=data['id'])
        channel.listener = data['listener']
        channel.save()

    def show_metadata(self, data):
        """
            value={'name': mount, 'key': key, 'val': val}
        """
        channel = Channel.objects.get(cluster=data['name'].split("-")[0])

        # mapping internal keys to attributes of stream channel
        map2channel = {'name': 'streamShow', 'genre': 'streamGenre',
                       'current_song': 'streamCurrentSong',
                       'description': 'streamDescription', 'url': 'streamURL'}
        if data['key'] in map2channel:
            setattr(channel, map2channel[data['key']], data['val'])
            channel.save()
        else:
            error_handler(
                "show_metadata: key %s not in channel map" % data['key'], channel)

        # mapping between internal keys and episode fields
        map2eps = {'name': 'title', 'description': 'description', 'url': 'url'}

        if channel.currentEpisode:
            episode = channel.currentEpisode
            part = episode.current_part
            if data['key'] == 'name' and data['val'].lower().startswith(episode.slug):
                data['val'] = data['val'][len(episode.slug):].strip()
            if data['key'] == 'url' and data['val'] != '':
                data['val'] = url_normalize(data['val'])
            if data['key'] in map2eps:
                setattr(part, map2eps[data['key']], data['val'])
                part.save()
        else:
            error_handler(
                "show_metadata: no current episode for %s" % channel.cluster, channel)

    def graphic_created(self, data):
        """
            value={'show': show, 'file': name})
        """
        cpwd = data['show'].split("-")[0]
        channel = Channel.objects.get(cluster=cpwd)

        g = Graphic(file='graphics/%s' % data['file'])

        if channel.currentEpisode:
            g.episode = channel.currentEpisode.current_part
        else:
            error_handler(
                "graphic_create: no current episode for %s" % channel.cluster, channel)

        g.save()

    def recording_start(self, data):
        cpwd = data["cluster"]

        channel = Channel.objects.get(cluster=cpwd)
        if channel.currentEpisode:
            part = channel.currentEpisode.current_part
        else:
            error_handler("recording_start: no current episode for %s" %
                         channel.cluster, channel)
            return

        r = Recording(episode=part)
        r.path = data['file']
        r.format = data['format']
        r.bitrate = data['bitrate']
        r.size = 0
        r.running = True
        r.save()

    def recording_stop(self, data):
        rec = Recording.objects.get(path=data['file'])
        rec.running = False
        rec.size = data['size']
        rec.save()

    def objects_get(self, data):
        type = ContentType.objects.get(
            app_label="radioportal", model=data['model'])
        model = type.model_class()
        name = model._meta.object_name.lower()
        if name not in dto_map:
            return
        objects = model.objects.all()
        Serializer = dto_map[name]
        plain_dict = []
        for o in objects:
            so = Serializer(o)
            plain_dict.append(so.__dict__)
        routing_key = "%s.%s.%s" % (
            model._meta.app_label, model._meta.module_name, "changed")

        self.reply(routing_key, plain_dict)
        logger.debug("Object list sent")
        # TODO: issue rpc call in backend
        # return plain_dict

    def feed_updated(self, data):
        if data['global']['type'] == 'calendar':
            try:
                show = Show.objects.get(slug=data['showid'])
            except Show.DoesNotExist:
                return
            for id, e in data['entries'].iteritems():
                slug = e['title'].split()[0]  # get first word from title
                slug = re.sub("\W", "", slug)  # remove non alpha numeric chars
                try:
                    ep = Episode.objects.get(
                        show=show, slug=slug, status=Episode.STATUS[2][0])
                except Episode.DoesNotExist:
                    ep = Episode(
                        show=show, slug=slug, status=Episode.STATUS[2][0])
                    ep.save()
                    epp = EpisodePart(episode=ep)
                    epp.begin = dateutil.parser.parse(
                        e['begin'], ignoretz=True)
                    epp.save()
                    ep.current_part = epp
                    ep.save()
                epp = ep.current_part
                epp.begin = dateutil.parser.parse(e['begin'], ignoretz=True)
                if 'end' in e:
                    epp.end = dateutil.parser.parse(e['end'], ignoretz=True)
                if 'url' in e:
                    epp.url = e['url']
                if 'description' in e:
                    epp.description = e['description'][:200]
                title = e['title'].split(None, 1)
                if len(title) == 2:
                    epp.title = title[1]
                else:
                    epp.title = ""
                epp.save()
        elif data['global']['type'] == 'podcast':
            try:
                show = Show.objects.get(slug=data['showid'])
            except Show.DoesNotExist:
                return
            limit = {'url': 180, 'description': 180, 'abstract': 400}
            for item in ('url', 'description', 'abstract'):
                if item in data['global']:
                    setattr(show, item, data['global'][item][:limit[item]])
            show.save()
            if 'icon' in data['global']:
                # print "got icon url: ", data['global']['icon']
                fetch_icon = True
                if show.icon:
                    # print "existing icon"
                    local_modtime = show.icon.get_source_modtime()
                    request = urllib2.Request(data['global']['icon'])
                    request.get_method = lambda: 'HEAD'
                    response = urllib2.urlopen(request)
                    time_s = response.headers['last-modified']
                    time_d = dateutil.parser.parse(time_s)
                    remote_modtime = time_d.strftime("%s")
                    # print "local time", local_modtime
                    # print "remote time", remote_modtime
                    # print "comparison: ", (int(remote_modtime) <=
                    # int(local_modtime))
                    if int(remote_modtime) <= int(local_modtime):
                        # print "don't fetch"
                        fetch_icon = False
                # print "fetch icon: ", fetch_icon
                if fetch_icon:
                    fname = urlparse.urlsplit(
                        data['global']['icon']).path.split("/")[-1]
                    path = show._meta.get_field_by_name("icon")[0].upload_to
                    fname = os.path.join(settings.MEDIA_ROOT,
                                         path, "%s-%s" % (show.slug, fname))
                    # print "name to save to:", fname
                    file, info = urllib.urlretrieve(
                        data['global']['icon'], fname)
                    # print "retrieve result: ", file, info
                    options = show._meta.get_field_by_name(
                        "icon")[0].resize_source
                    thumbnailer = easy_thumbnails.files.get_thumbnailer(file)
                    content = thumbnailer.generate_thumbnail(options)
                    # print content
                    show.icon = content
                    show.save()


    @reversion.create_revision()
    def dispatch_message(self, routing_key, data):
        keys = routing_key.split(".", 1)
        if len(keys) != 2:
            msg = "routing_key %s too short" % routing_key
            logger.warning(msg)
            return
        logger.debug("calling bi.%s_%s(data)" % (keys[0], keys[1]))

        if not hasattr(self, '%s_%s' % (keys[0], keys[1])):
            msg = "No method for routing_key %s" % routing_key
            logger.debug(msg)
            return
        try:
            return getattr(self, '%s_%s' % (keys[0], keys[1]))(data)
        except Exception as inst:
            print traceback.format_exc()
            logger.exception(inst)
            connection._rollback()
            raise inst
