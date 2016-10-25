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

from django.utils.datetime_safe import datetime
from django.contrib.contenttypes.models import ContentType

from django.db import connection
from django.conf import settings
from django.core.files.base import ContentFile

import traceback
import logging
logger = logging.getLogger(__name__)

import base64
import copy
import easy_thumbnails.files
import os.path
import time
import re
import urllib
import urllib2
import urlparse
import uuid
import simplejson
from lxml import etree
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from easy_thumbnails.files import generate_all_aliases


from radioportal.models import Channel, Episode, EpisodePart, Stream, Graphic, Recording, Show, Message, ICalEpisodeSource, PodcastFeed

# from radioportal_auphonic.models import AuphonicSettings

from radioportal.url_normalize import url_normalize

import dateutil.parser

from .send import dto_map, send_msg, serialize_object
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
            obj = Show.objects.get(slug=data["show"])
        if "stamp" in data:
            d = dateutil.parser.parse(data['stamp'])
        else:
            d = None
        if "path" in data:
            m=Message(message_object=obj, origin=data["path"], message=data["message"],
                      severity=data["level"], timestamp=d)
        else:
            m=Message(message_object=obj, origin=data["component"], message=str(data["context"]),
                      severity=data["level"], timestamp=d)
        m.save()

    def channel_startmaster(self, data):
        """
            value={'name': cpwd, 'time': int, 'show' : {'name': 'CR001 Titel der Sendung'}}
            data={"name": "event", "metadata": {"url": "", "genre": "various", "description": "Unspecified description", "name": "event139 Stream mit Uml\u00e4ut \u00fc\u00f6\u00e4\u00dc\u00d6\u00c4\u00df\u00f8\u00d8"}}
            FIXME: need show
        """
        channel = Channel.objects.get(cluster=data['name'])

        available_methods = get_episode_finder()
        episode = None

        methods = copy.copy(channel.mapping_method)
        methods.append("make-live")

        for method in methods:
            # print "trying method", method
            if method not in available_methods:
                error_handler("Mapping method %s not found" % method, channel)
                continue
            finder = available_methods[method]()
            try:
                episode = finder.get_episode(channel, data['metadata'])
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

        self._update_metadata(channel, data["metadata"])

        channel.save()

        episode_serialized = serialize_object(episode)
        episode_ser = simplejson.loads(episode_serialized)[0]

        data = {'name': data['name'], 'metadata': {'episode': episode_ser} } 

        print "Sending msg channel.update", data        
        send_msg("channel.update", simplejson.dumps(data), exchange="backenddata")
        print "sent msg"

    def channel_stop(self, data):
        """
            value={'name': cpwd}
            data={"name": "event"}
        """
        channel = Channel.objects.get(cluster=data['name'])
        if channel.currentEpisode:
            episode = channel.currentEpisode
            part = episode.current_part
            if part:
                part.end = datetime.now()
                part.save()
            else:
                error_handler("channel_stop: no current part found for cluster %s" %
                         data['name'], channel)
            episode.current_part = None
            episode.status = Episode.STATUS[0][0]
            episode.save()
            channel.currentEpisode = None
            channel.save()
        else:
            error_handler("channel_stop: no current episode found for cluster %s" %
                         data['name'], channel)
            # FIXME

    def stream_start(self, data):
        """
            value={'name': mount, 'id': id, 'stream': {'mountpoint': 'mount.mp4', 'bitrate': 128, 'type': 'mp3'}}
            data={"url": "http://streams.xenim.de/event.mp3", "type": "http", "quality": 0, "name": "/event.mp3", "format": "mp3"}
            FIXME: Stream object
        """

        mp = data['name'][1:]

        stream = Stream.objects.get(mount=mp)

        stream.running = True
        stream.bitrate = data['quality']
        stream.transport = data['type']
        stream.codec = data['format']
        if stream.transport == "hls":
            stream.container = "mpegts"
        elif stream.codec in ("vorbis", "opus", "theora"):
            stream.container = "ogg"
        else:
            stream.container = "none"
        stream.save()
        # stream.channel.updateRunning()

    def stream_stop(self, data):
        """
            value={'name': mount}
            value={"name": "/event.mp3"}
        """
        mount = data['name'][1:]

        stream = Stream.objects.get(mount=mount)

        stream.running = False
        stream.save()

    def channel_listeners(self, data):
        """
            data={"listeners": 1, "name": "event"}
        """
        channel = Channel.objects.get(cluster=data['name'])
        channel.listener = data['listeners']
        channel.save()

    def channel_metadata(self, data):
        """
            value={'name': mount, 'key': key, 'val': val}
        """
        channel = Channel.objects.get(cluster=data['name'].split("-")[0])

        self._update_metadata(channel, {data['key']: data['val']})


    def _update_metadata(self, channel, metadata):

        # mapping internal keys to attributes of stream channel
        map2channel = {'name': 'streamShow', 'genre': 'streamGenre',
                       'current_song': 'streamCurrentSong',
                       'description': 'streamDescription', 'url': 'streamURL'}
        for key, value in metadata.iteritems():
            if key in map2channel:
                setattr(channel, map2channel[key], value)
            else:
                error_handler(
                    "show_metadata: key %s not in channel map" % key, channel)
        channel.save()

        # mapping between internal keys and episode fields
        map2eps = {'name': 'title', 'description': 'description', 'url': 'url'}

        if channel.currentEpisode:
            episode = channel.currentEpisode
            part = episode.current_part
            for key, value in metadata.iteritems():
                if key == 'name' and value.lower().startswith(episode.slug):
                    value = value[len(episode.slug):].strip()
                if key == 'url' and value != '':
                    value = url_normalize(value)
                if key in map2eps:
                    setattr(part, map2eps[key], value)
                    part.save()
        else:
            error_handler(
                "show_metadata: no current episode for %s" % channel.cluster, channel)

    def graphic_updated(self, data):
        channel = Channel.objects.get(cluster=data["channel"])

        if not channel.currentEpisode or not channel.currentEpisode.current_part:
            if "episode" in data:
                episode_slug = data["episode"].split("-")[-1]
                episode = Episode.objects.filter(slug=episode_slug)
                if len(episode) == 1:
                    episode = episode[0]
                    if len(episode.parts.all()) == 1:
                        part = episode.parts.all()[0]
                    elif "begin" in data:
                        begin = int(data["begin"])
                        begindt = datetime.fromtimestamp(begin)
                        for p in episode.parts.all():
                            if abs((p.begin()-begindt).seconds) < 120:
                                part = p
            if not part:
                error_handler("graphic_update: no current episode for %s" % channel.cluster, channel)
                return
        else:
            part = channel.currentEpisode.current_part

        g, created = Graphic.objects.get_or_create(type=data["type"], episode=part)
        if "image" in data:
            if created:
                g.file.save("", ContentFile(base64.b64decode(data["image"])))
            else:
                f = open(g.file.path, "w")
                f.write(base64.b64decode(data["image"]))
                f.close()
        elif "data" in data:
            g.data = data["data"]
            g.save()

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
        #r.format = data['format']
        #r.bitrate = data['bitrate']
        r.size = 0
        r.running = True
        r.save()

    def recording_stop(self, data):
        rec = Recording.objects.get(path=data['file'])
        rec.running = False
        rec.size = data['size']
        rec.save()

    def objects_get(self, data):
        try:
            type = ContentType.objects.get(
                app_label="radioportal", model=data['model'])
        except ContentType.DoesNotExist:
            return
        model = type.model_class()
        name = model._meta.object_name.lower()
        if name not in dto_map:
            return
        objects = model.objects.all()
        Serializer = dto_map[name]
        plain_dict = []
        for o in objects:
            so = Serializer(o)
            if so:
                plain_dict.append(so.__dict__)
        routing_key = "%s.%s.%s" % (
            model._meta.app_label, model._meta.model_name, "changed")

        logger.debug("Object list sent")
        # TODO: issue rpc call in backend
        return (routing_key, plain_dict)

    def importer_ical(self, data):
        try:
            show = Show.objects.get(slug=data['show'])
        except Show.DoesNotExist:
            return

        for uid, e in data['entries'].iteritems():
            if not ICalEpisodeSource.objects.filter(identifier=uid).count():
                source = ICalEpisodeSource(identifier=uid, source=show.icalfeed)
                source.save()
                ep = Episode(show=show, source=source, slug=e["slug"], status=Episode.STATUS[2][0])
                ep.save()
                epp = EpisodePart(episode=ep)
                epp.begin = dateutil.parser.parse(
                    e['begin'], ignoretz=True)
                epp.save()
                ep.current_part = epp
                ep.save()
            else:
                source = ICalEpisodeSource.objects.get(identifier=uid)
                try:
                    ep = source.episode
                except Episode.DoesNotExist:
                    text = "No episode created for uid %s as the previously" \
                           " created episode was deleted" % uid
                    m = Message(message_object=show, origin="importer.ical", 
                                message=text, severity=3)
                    m.save()
                    continue

            ep.slug = e["slug"]
            ep.save()

            epp = ep.current_part
            epp.begin = dateutil.parser.parse(e['begin'], ignoretz=True)
            if 'end' in e:
                epp.end = dateutil.parser.parse(e['end'], ignoretz=True)
            if 'url' in e:
                epp.url = e['url']
            if 'description' in e:
                epp.description = e['description'][:200]
            if "title" in e:
                epp.title = e["title"]
            epp.save()
        if show.icalfeed.delete_missing and False:
            ICalEpisodeSource.objects.exclude(identifier__in=data['entries'].keys()).filter(episode__status="UPCOMING").delete()

    def podcast_feed(self, data):
        tree = etree.fromstring(data["content"])
        pf = PodcastFeed.objects.get(show__slug=data["show"])
        show = pf.show
        for field, value in filter(lambda x: x[0].endswith("_enabled"), vars(pf).iteritems()):
            # print field, value
            if not value:
                continue
            if field[:-8] + "_xpath" in vars(pf):
                xpath = vars(pf)[field[:-8] + "_xpath"]
                value = tree.xpath(xpath, namespaces=tree.nsmap)
                if not value:
                    continue
                value = value[0]
            regex = None
            if field[:-8] + "_regex" in vars(pf):
                regex = vars(pf)[field[:-8] + "_regex"]
            if regex:
                match = re.search(regex,value)
                if match and "value" in match.groupdict():
                    value = match.group("value")
            # print field[:-8], value
            if field[:-8] == "icon":
                headers = {}
                local_modtime = None
                if os.path.exists(show.icon.path):
                    if show.icon_url == value and show.icon_etag:
                        headers["If-None-Match"] = show.icon_etag
                    local_modtime = os.path.getmtime(show.icon.path)
                    headers["If-Modified-Since"] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.localtime(local_modtime))
                r = requests.head(value, headers=headers)
                if r.status_code == 200:
                    if local_modtime and "last-modified" in r.headers:
                        time_s = r.headers['last-modified']
                        time_d = dateutil.parser.parse(time_s)
                        remote_modtime = int(time_d.strftime("%s"))
                        if remote_modtime < local_modtime:
                            continue
                    r = requests.get(value, headers=headers)
                    if r.status_code != 200:
                        continue
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(r.content)
                    img_temp.flush()
                    show.icon.save("%s.jpg" % show.slug, File(img_temp), save=True)
                    generate_all_aliases(show.icon, include_global=True)
                    if "etag" in r.headers:
                        show.icon_etag = r.headers["etag"]
                    show.icon_url = r.url
                    show.save()
            else:
                setattr(show, field[:-8], value)
        show.save()


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
