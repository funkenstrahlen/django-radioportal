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

from django.db.models.signals import post_save, post_delete
from django.core.serializers import json
from django.conf import settings

from radioportal.models import SourcedStream, ShowFeed, RecodedStream

import simplejson

from carrot.connection import DjangoBrokerConnection, BrokerConnection
from carrot.messaging import Publisher

#### Part one: sending notifications for changed objects ####


class DTO(object):
    def serialize(self):
        return simplejson.dumps((self.__dict__,))


class DTOSourcedStream(DTO):
    def __init__(self, instance):
        self.mount = instance.mount
        self.user = instance.user
        self.password = instance.password
        self.encoding = instance.encoding
        self.cluster = instance.channel.cluster
        self.recording = instance.channel.recording
        self.fallback = instance.fallback
        self.id = instance.pk


class DTOShowFeed(DTO):
    def __init__(self, instance):
        self.enabled = instance.enabled
        self.feed = instance.feed
        self.ical = instance.icalfeed
        self.title_regex = instance.titlePattern
        self.show = instance.show.slug
        self.id = instance.pk


class DTOShow(DTO):
    def __init__(self, instance):
        self.slug = instance.slug
        self.cluster = instance.channel.cluster
        self.twitter = instance.twitter
        self.chat = instance.chat


class DTOAuphonic(DTO):
    def __init__(self, instance):
        self.channel = instance.channel.cluster
        if instance.preset:
            self.preset = instance.preset.uuid
        else:
            self.preset = ""
        self.update_md = instance.update_metadata
        self.enabled = instance.enabled
        self.oauth_token = instance.oauth_token
        self.id = self.channel

dto_map = {
    "sourcedstream": DTOSourcedStream,
    "showfeed": DTOShowFeed,
    #"auphonicsettings": DTOAuphonic,
}



def send_msg(routing_key, data):
    conn = BrokerConnection(
                hostname=settings.BROKER_HOST,
                port=settings.BROKER_PORT,
                userid=settings.BROKER_USER,
                password=settings.BROKER_PASSWORD,
                virtual_host=settings.BROKER_VHOST)
    publisher = Publisher(connection=conn,
                          exchange="django_send",
                          routing_key=routing_key,
                          exchange_type="topic",
                          )
    publisher.send(data)
    publisher.close()
    conn.close()

class AMQPInitMiddleware(object):

    sender_callback = None

    def __init__(self):

        logger.info("Connecting model change signals to amqp")

        print "Connecting model change signals to amqp"

        for m in (RecodedStream, SourcedStream, ShowFeed):
            post_save.connect(
                self.object_changed, m, dispatch_uid="my_dispatch_uid")
            post_delete.connect(
                self.object_deleted, m, dispatch_uid="my_dispatch_uid")

    def serialize(self, instance):
        name = instance._meta.object_name.lower()
        if name in dto_map:
            return dto_map[name](instance).serialize()
        else:
            return json.Serializer().serialize((instance,))

    def sender_callback(self, routing_key, data):
        send_msg(routing_key, data)
        print "Sent object change/delete message for %s" % routing_key

    def object_changed(self, sender, instance, created, **kwargs):
        action = "created" if created else "changed"
        routing_key = "%s.%s.%s" % (
            sender._meta.app_label, sender._meta.module_name, action)
        data = self.serialize(instance)
        self.sender_callback(routing_key, data)
        logger.debug("Object change message for %s sent" % unicode(instance))

    def object_deleted(self, sender, instance, **kwargs):
        routing_key = "%s.%s.deleted" % (
            sender._meta.app_label, sender._meta.module_name)
        data = self.serialize(instance)
        self.sender_callback(routing_key, data)
        logger.debug("Object delete message for %s sent" % unicode(instance))

    def process_request(self, request):
        """ Dummy method to keep object in scope """
        return None
