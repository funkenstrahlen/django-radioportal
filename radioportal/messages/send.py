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


import logging
logger = logging.getLogger(__name__)

from django.db.models.signals import post_save, post_delete, pre_delete
from django.core.serializers import json
from django.conf import settings

from radioportal.models import SourcedStream, ShowFeed, Show, ICalFeed, Channel, RecodedStream, PrimaryNotification, SecondaryNotification

from extshorturls.utils import ShortURLResolver

import simplejson

#if settings.AMQP:
import pika

#### Part one: sending notifications for changed objects ####

shorturls = ShortURLResolver()

class DTO(object):
    def name():
        return None

    def serialize(self):
        return simplejson.dumps((self.__dict__,))


class DTOChannel(DTO):
    def name(self):
        return "channel"

    def __init__(self, instance):
        self.id = instance.cluster
        self.recording = instance.recording
        self.public_recording = instance.public_recording
        if hasattr(instance, "auphonic"):
            self.auphonic= {}
            self.auphonic['enabled'] = instance.auphonic.enabled
            self.auphonic['oauth_token'] = instance.auphonic.oauth_token
            self.auphonic['update_metadata'] = instance.auphonic.update_metadata
            self.auphonic['preset'] = instance.auphonic.preset
        self.episode = {}
        if instance.currentEpisode:
            self.episode = DTOEpisode(instance.currentEpisode).serialize()


class DTOSourcedStream(DTO):
    def name(self):
        return "sourcedstream"

    def __init__(self, instance):
        self.mount = instance.mount
        self.user = instance.user
        self.password = instance.password
        self.encoding = instance.encoding
        self.channel = instance.channel.cluster
        self.fallback = instance.fallback
        self.id = instance.mount
        self.recode = []
        for rs in instance.recoded.all():
            self.recode.append({'mount': rs.mount, 'format': rs.format, 'bitrate': rs.bitrate})


class DTORecodedStream(DTOSourcedStream):
    def __init__(self, instance):
        super(DTORecodedStream, self).__init__(instance.source)


class DTOShow(DTO):
    def name(self):
        return "show"

    def __init__(self, instance):
        self.id = instance.slug
        self.twitter = instance.twitter
        self.chat = instance.chat
        if hasattr(instance, "showtwitter"):
            self.twitter_token = instance.showtwitter.token
            self.twitter_secret = instance.showtwitter.secret
        if hasattr(instance, "showfeed"):
            self.feed = {}
            self.feed['enabled'] = instance.showfeed.enabled
            self.feed['feed'] = instance.showfeed.feed
            self.feed['icalfeed'] = instance.showfeed.icalfeed
            self.feed['titlePattern'] = instance.showfeed.titlePattern
        if hasattr(instance, "icalfeed") and instance.icalfeed.enabled:
            self.ical = {}
            self.ical["url"] = instance.icalfeed.url
            self.ical["fields"] = []
            if instance.icalfeed.slug_regex:
                self.ical["fields"].append((
                    "slug",
                    instance.icalfeed.slug_field,
                    instance.icalfeed.slug_regex.format(show=instance),
                ))
            if instance.icalfeed.title_regex:
                self.ical["fields"].append((
                    "title",
                    instance.icalfeed.title_field,
                    instance.icalfeed.title_regex.format(show=instance),
                ))
            if instance.icalfeed.description_regex:
                self.ical["fields"].append((
                    "description",
                    instance.icalfeed.description_field,
                    instance.icalfeed.description_regex.format(show=instance),
                ))
            if instance.icalfeed.url_regex:
                self.ical["fields"].append((
                    "url",
                    instance.icalfeed.url_field,
                    instance.icalfeed.url_regex.format(show=instance),
                ))
            if instance.icalfeed.filter_regex:
                self.ical["filter"] = [
                    (
                        instance.icalfeed.filter_field,
                        instance.icalfeed.filter_regex,
                    ),
                ]
        self.notifications = []
        for pn in instance.primarynotification_set.all():
            noti = {
                'start': pn.start.text,
                'stop': pn.stop.text,
                'rollover': pn.rollover.text,
                'type': pn.path.name(),
            }
            if pn.path.name() == "twitter":
                noti['token'] = pn.path.get().oauth_token
                noti['secret'] = pn.path.get().oauth_secret
                noti['secondary'] = []
                for sn in pn.secondarynotification_set.all():
                    noti['secondary'].append({
                        'type': sn.path.name(),
                        'token': sn.path.get().oauth_token,
                        'secret': sn.path.get().oauth_secret,
                    })
            elif pn.path.name() in ("irc", "http"):
                noti["url"] = pn.path.get().url
            elif pn.path.name() == "auphonic":
                noti["access_token"] = pn.path.get().access_token
                noti["preset"] = pn.path.get().preset
                noti["start_production"] = pn.path.get().start_production
            self.notifications.append(noti)


class DTOShowTwitter(DTOShow):
    def __init__(self, instance):
        super(DTOShowTwitter, self).__init__(instance.show)

class DTOShowFeed(DTOShow):
    def __init__(self, instance):
        super(DTOShowFeed, self).__init__(instance.show)

class DTOIcalFeed(DTOShow):
    def __init__(self, instance):
        super(DTOIcalFeed, self).__init__(instance.show)

class DTOPrimaryNotification(DTOShow):
    def __init__(self, instance):
        super(DTOPrimaryNotification, self).__init__(instance.show)

class DTOSecondaryNotification(DTOShow):
    def __init__(self, instance):
        super(DTOSecondaryNotification, self).__init__(instance.show)

class DTOEpisode(DTO):
    def name(self):
        return "episode"

    def __init__(self, instance):
        self._id = instance.id
        if instance.current_part:
            self._part_id = instance.current_part.id
        self.slug = instance.get_id()
        self.show = instance.show.slug
        self.url = instance.get_absolute_url()
        self.url_s = shorturls.get_shorturl(instance)

dto_map = {
    "sourcedstream": DTOSourcedStream,
    "recodedstream": DTORecodedStream,
    "show": DTOShow,
    "showfeed": DTOShowFeed,
    "showtwitter": DTOShowTwitter,
    "primarynotification": DTOPrimaryNotification,
    "secondarynotification": DTOSecondaryNotification,
    "icalfeed": DTOIcalFeed,
    "episode": DTOEpisode,
    "channel": DTOChannel,
}


def send_msg(routing_key, data, exchange="django_send"):
    credentials = pika.PlainCredentials(
        username=settings.BROKER_USER,
        password=settings.BROKER_PASSWORD)
        
    parameters = pika.ConnectionParameters(
                host=settings.BROKER_HOST,
                port=settings.BROKER_PORT,
                virtual_host=settings.BROKER_VHOST,
                credentials=credentials,
                ssl=bool(settings.BROKER_SSL))

    conn = pika.BlockingConnection(parameters)
    channel = conn.channel()

    prop = pika.BasicProperties(content_type='text/plain',
                                delivery_mode=1)
    channel.basic_publish(exchange, routing_key, data, prop)
    conn.close()



# def send_msg_carrot(routing_key, data, exchange="django_send"):
#     conn = BrokerConnection(
#                 hostname=settings.BROKER_HOST,
#                 port=settings.BROKER_PORT,
#                 userid=settings.BROKER_USER,
#                 password=settings.BROKER_PASSWORD,
#                 virtual_host=settings.BROKER_VHOST)
#     publisher = Publisher(connection=conn,
#                           exchange=exchange,
#                           routing_key=routing_key,
#                           exchange_type="topic",
#                           )
#     publisher.send(data)
#     publisher.close()
#     conn.close()


def serialize_object(instance, return_name=False):
    name = instance._meta.object_name.lower()
    if name in dto_map:
        dto = dto_map[name](instance)
        if return_name:
            return (dto.serialize(), dto.name())
        else:
            return dto.serialize()
    else:
        return json.Serializer().serialize((instance,))


class AMQPInitMiddleware(object):

    sender_callback = None

    def __init__(self):

        logger.info("Connecting model change signals to amqp")

        print "Connecting model change signals to amqp"

        for m in (RecodedStream, SourcedStream, ShowFeed, ICalFeed, Show, Channel, PrimaryNotification, SecondaryNotification):
            post_save.connect(
                self.object_changed, m, dispatch_uid="my_dispatch_uid")
            pre_delete.connect(
                self.object_deleted, m, dispatch_uid="my_dispatch_uid")

    def sender_callback(self, routing_key, data):
        send_msg(routing_key, data)
        print "Sent object change/delete message for %s" % routing_key

    def object_changed(self, sender, instance, created, **kwargs):
        action = "created" if created else "changed"
        data, name = serialize_object(instance, True)
        routing_key = "%s.%s.%s" % (sender._meta.app_label, name, action)
        self.sender_callback(routing_key, data)
        logger.debug("Object change message for %s sent" % unicode(instance))

    def object_deleted(self, sender, instance, **kwargs):
        routing_key = "%s.%s.deleted" % (
            sender._meta.app_label, sender._meta.object_name.lower())
        data = serialize_object(instance)
        self.sender_callback(routing_key, data)
        logger.debug("Object delete message for %s sent" % unicode(instance))

    def process_request(self, request):
        """ Dummy method to keep object in scope """
        return None
