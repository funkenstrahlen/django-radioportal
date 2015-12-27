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
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from django.conf import settings

from radioportal.dashboard import views, forms, notification, importer, debug

import django.contrib.auth.views
django.contrib.auth.views.is_safe_url=views.is_safe_url

from django_hosts import reverse_lazy, reverse_host_lazy

from django.contrib import admin
admin.autodiscover()


wizard_forms = [forms.UserWizardForm, forms.ShowWizardForm, forms.ChannelWizardForm, forms.StreamWizardForm]

urlpatterns = patterns('',
    #url(r'^auphonic/', include('radioportal_auphonic.urls')),
    #url(r'^control/', include('radioportal_control.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n', 'django.views.i18n.javascript_catalog', name="jsi18n"),

    url(r'^$', views.LandingView.as_view(), name="dashboard"),

    url(r'^perm/(?P<model>[\w]+)/(?P<user_name>[\w-]+)/$', views.PermissionChangeView.as_view(), name="admin-perm"),

    url(r'^wizard/(?P<id>[0-9]+)/$', views.UserChannelStreamAddView.as_view(wizard_forms), name="admin-wizard-id"),
    url(r'^wizard/$', views.UserChannelStreamAddView.as_view(wizard_forms), name="admin-wizard"),

    url(r'^user/$', views.UserGroupListView.as_view(), name="admin-list-users"),
    url(r'^user/create/$', views.UserCreateView.as_view() , name="admin-user-create"),
    url(r'^user/(?P<slug>[\w-]+)/$', views.UserEditView.as_view(), name="admin-user-edit"),

    url(r'^group/create/$', views.GroupCreateView.as_view(), name="admin-group-create"),
    url(r'^group/(?P<slug>[\w-]+)/$', views.GroupEditView.as_view(), name="admin-group-edit"),

    url(r'^show/create/$', views.ShowCreateView.as_view(), name="admin-show-create"),
    url(r'^show/(?P<slug>[\w-]+)/$', views.EpisodeListView.as_view(), name="admin-episode-list"),
    url(r'^show/(?P<slug>[\w-]+)/edit/$', views.ShowEditView.as_view(), name="admin-show-edit"),
    url(r'^show/(?P<slug>[\w-]+)/delete/$', views.ShowDeleteView.as_view(), name="admin-show-delete"),
    url(r'^show/(?P<slug>[\w-]+)/feed/$', views.PodcastFeedEditView.as_view(), name="admin-show-feed"),
    url(r'^show/(?P<slug>[\w-]+)/ical/$', importer.ICalEditView.as_view(), name="admin-show-ical"),
    url(r'^show/(?P<slug>[\w-]+)/create-episode/$', views.EpisodeCreateView.as_view(), name="admin-episode-create"),
    url(r'^show/(?P<slug>[\w-]+)/notification/$', notification.NotificationListView.as_view(), name="admin-show-notification"),
    url(r'^show/(?P<slug>[\w-]+)/notification/twitter/(?P<path>(primary|secondary))/$', notification.twitter_gettoken, name="admin-show-notification-twitter"),
    url(r'^show/(?P<slug>[\w-]+)/notification/twitter/(?P<path>(primary|secondary))/cb/$', notification.twitter_callback, name="admin-show-notification-twitter-callback"),
    url(r'^show/(?P<slug>[\w-]+)/notification/auphonic/$', notification.auphonic_gettoken, name="admin-show-notification-auphonic"),
    url(r'^show/(?P<slug>[\w-]+)/notification/auphonic/cb/$', notification.auphonic_callback, name="admin-show-notification-auphonic-callback"),
    url(r'^show/(?P<slug>[\w-]+)/notification/s-(?P<nslug>[\w-]+)/delete/$', notification.DeleteSecondaryNotificationView.as_view(), name="admin-show-secondary-notification-delete"),
    url(r'^show/(?P<slug>[\w-]+)/notification/(?P<nslug>[\w-]+)/delete/$', notification.DeleteNotificationView.as_view(), name="admin-show-notification-delete"),
    url(r'^show/(?P<slug>[\w-]+)/notification/(?P<path>(irc|http))/add/$', notification.CreateNotificationView.as_view(), name="admin-show-notification-create"),
    url(r'^show/(?P<slug>[\w-]+)/notification/s-(?P<path>(twitter))/(?P<nslug>[\w-]+)/$', notification.UpdateSecondaryNotificationView.as_view(), name="admin-show-secondary-notification-edit"),
    url(r'^show/(?P<slug>[\w-]+)/notification/(?P<path>(twitter|irc|http|auphonic))/(?P<nslug>[\w-]+)/$', notification.UpdateNotificationView.as_view(), name="admin-show-notification-edit"),

    url(r'^episode/(?P<pk>[\w-]+)/$', views.EpisodeEditView.as_view(), name="admin-episode-edit"),
    url(r'^episode/(?P<pk>[\w-]+)/delete/$', views.EpisodeDeleteView.as_view(), name="admin-episode-delete"),

    url(r'^episodepart/(?P<pk>[\w-]+)/$', views.EpisodePartEditView.as_view(), name="admin-episodepart-edit"),

    url(r'^channel/create/$', views.ChannelCreateView.as_view(), name="admin-channel-create"),
    url(r'^channel/(?P<pk>[\w-]+)/$', views.ChannelEditView.as_view(), name="admin-channel-edit"),
    url(r'^cluster/(?P<slug>[\w-]+)/$', views.ChannelClusterEditView.as_view(), name="admin-channel-edit-cluster"),
    url(r'^channel/(?P<pk>[\w-]+)/delete/$', views.ChannelDeleteView.as_view(), name="admin-channel-delete"),
    url(r'^channel/(?P<pk>[\w-]+)/cce/$', views.ChannelChangeCurrentEpisode.as_view(), name="admin-channel-cce"),

    
    url(r'^accounts/login/$', django.contrib.auth.views.login, {}, name="login"),
    url(r'^accounts/logout/$', django.contrib.auth.views.logout_then_login, {}, name="logout"),
    url(r'^accounts/change-password/$', django.contrib.auth.views.password_change, {'template_name': 'registration/password_change.html'}),
    url(r'^accounts/changed-password/$', django.contrib.auth.views.password_change_done, {'template_name': 'registration/password_changed.html'}, name="password_change_done"),

    url(r'^accounts/reset-password/$', django.contrib.auth.views.password_reset, {'post_reset_redirect': reverse_lazy('password_reset_done', host="dashboard")}),
    url(r'^accounts/reset-password/sent/$', django.contrib.auth.views.password_reset_done, name="password_reset_done"),
    url(r'^accounts/reset-password/(?P<uidb64>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', django.contrib.auth.views.password_reset_confirm, name="password_reset_confirm"),
    url(r'^accounts/reset-password/done/$', django.contrib.auth.views.password_reset_complete, name="password_reset_complete"),

    url(r'^icecast/source-auth/$', views.icecast_source_auth),
    url(r'^icecast/sandbox-lauth/$', views.icecast_sandbox_lauth),
    url(r'^messages/$', views.MessageListView.as_view(), name="admin-messages-list"),
)
if settings.DEBUG:
    urlpatterns += patterns('', 
        url(r'^debug/fake-stream/$', debug.FakeStreamView.as_view(), name='debug-fake-stream'),
    )
