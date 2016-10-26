# -*- encoding: utf-8 -*-
#
# Copyright © 2016 Robert Weidlich. All Rights Reserved.
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

import re

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from django_hosts.resolvers import reverse
from guardian.shortcuts import assign
import allauth.account.signals

from radioportal.models import Show, ShowRequest, Channel, SourcedStream
from radioportal import util


@receiver(allauth.account.signals.email_confirmed)
def email_confirmed_(email_address, **kwargs):
    user = email_address.user
    requests = ShowRequest.objects.filter(user=user, status="UNCONFIR")
    for sr in requests:
        sr.status = "NEW"
        sr.save()


@receiver(post_save, sender=ShowRequest)
def handle_request(sender, instance, created, raw, *args, **kwargs):
    if raw:
        return
    if instance.status == "NEW":
        for user in util.get_users_by_permission("radioportal.change_showrequest", False):
            mail_data = {
                'request_url': reverse('admin-show-request', kwargs={'pk': instance.id}, host='dashboard'),
            }
            mail_text = render_to_string("radioportal/dashboard/new_request.txt", mail_data)
            mail_subject = _("[xenim] New Request for Show")

            send_mail(mail_subject, mail_text, "noreply@streams.xenim.de", [user.email, ])
    elif instance.status == "ACCEPTED" and not instance.show:
        show = Show(name=instance.name)
        show.defaultShortName = re.sub("[^A-Z]", "", instance.name)
        if not show.defaultShortName:
            show.defaultShortName = instance.name[:2]
        show.save()
        instance.show = show
        instance.save()

        show.icalfeed.url = instance.ical
        show.icalfeed.enabled = True
        show.icalfeed.save()

        show.podcastfeed.feed_url = instance.feed
        show.podcastfeed.enabled = True
        show.podcastfeed.name_enabled = True
        show.podcastfeed.url_enabled = True
        show.podcastfeed.description_enabled = True
        show.podcastfeed.abstract_enabled = True
        show.podcastfeed.icon_enabled = True
        show.podcastfeed.public_email_enabled = True
        show.podcastfeed.donation_url_enabled = True
        show.podcastfeed.licence_enabled = True
        show.podcastfeed.save()

        channel = Channel(cluster=instance.name.lower())
        channel.mapping_method = '["find-from-title","make-from-title","find-or-make-live"]'
        channel.save()
        channel.show.add(show)

        stream = SourcedStream(mount="%s.mp3" % instance.name.lower())
        stream.user = "source"
        stream_pw = User.objects.make_random_password()
        stream.password = stream_pw
        stream.channel = channel
        stream.save()

        assign('radioportal.change_channel', instance.user, channel)
        assign('radioportal.change_stream', instance.user, channel)

        assign('radioportal.change_episodes', instance.user, show)
        assign('radioportal.change_show', instance.user, show)

        mail_data = {
            'show_url': reverse('admin-episode-list', kwargs={'slug': show.slug}, host='dashboard'),
            'wiki_url': reverse('landing', host='wiki'),
            'wiki_communication_url': reverse('wiki-category-page', kwargs={'category': 'project', 'page': 'communication'}, host='wiki'),
        }
        mail_text = render_to_string("radioportal/dashboard/showcreated_mail.txt", mail_data)
        mail_subject = _("[xenim] Created New Show")

        send_mail(mail_subject, mail_text, "noreply@streams.xenim.de", [instance.user.email, ])
