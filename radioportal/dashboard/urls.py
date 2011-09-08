# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from radioportal.dashboard import views
import django.contrib.auth.views

urlpatterns = patterns('',
    url(r'^$', views.LandingView.as_view(), name="dashboard"),

    url(r'^user/$', views.UserGroupListView.as_view(), name="admin-list-users"),
    url(r'^user/create/$', views.UserCreateView.as_view() , name="admin-user-create"),
    url(r'^user/(?P<slug>[\w-]+)/$', views.UserEditView.as_view(), name="admin-user-edit"),

    url(r'^group/create/$', views.GroupCreateView.as_view(), name="admin-group-create"),
    url(r'^group/(?P<slug>[\w-]+)/$', views.GroupEditView.as_view(), name="admin-group-edit"),

    url(r'^show/create/$', views.ShowCreateView.as_view(), name="admin-show-create"),
    url(r'^show/(?P<slug>[\w-]+)/$', views.EpisodeListView.as_view(), name="admin-episode-list"),
    url(r'^show/(?P<slug>[\w-]+)/edit/$', views.ShowEditView.as_view(), name="admin-show-edit"),
    url(r'^show/(?P<slug>[\w-]+)/delete/$', views.ShowDeleteView.as_view(), name="admin-show-delete"),
    url(r'^show/(?P<slug>[\w-]+)/feed/$', views.ShowFeedEditView.as_view(), name="admin-show-feed"),
    url(r'^show/(?P<slug>[\w-]+)/create-episode/$', views.EpisodeCreateView.as_view(), name="admin-episode-create"),

    url(r'^episode/(?P<pk>[\w-]+)/$', views.EpisodeEditView.as_view(), name="admin-episode-edit"),
    url(r'^episode/(?P<pk>[\w-]+)/delete/$', views.EpisodeDeleteView.as_view(), name="admin-episode-delete"),

    url(r'^streamsetup/create/$', views.StreamSetupCreateView.as_view(), name="admin-streamsetup-create"),
    url(r'^streamsetup/(?P<pk>[\w-]+)/$', views.StreamSetupEditView.as_view(), name="admin-streamsetup-edit"),
    url(r'^streamsetup/(?P<pk>[\w-]+)/delete/$', views.StreamSetupDeleteView.as_view(), name="admin-streamsetup-delete"),
    
    url(r'^accounts/login/$', django.contrib.auth.views.login, {}, name="login"),
    url(r'^accounts/logout/$', django.contrib.auth.views.logout_then_login, {}, name="logout"),
    url(r'^accounts/change-password/$', django.contrib.auth.views.password_change, 
    {'template_name': 'registration/password_change.html'}, name="account-change-pass"),
    url(r'^accounts/changed-password/$', django.contrib.auth.views.password_change_done, 
    {'template_name': 'registration/password_changed.html'}, name="account-changed-pass"),

    url(r'^accounts/reset-password/$', django.contrib.auth.views.password_reset),
    url(r'^accounts/reset-password/sent/$', django.contrib.auth.views.password_reset_done),
    url(r'^accounts/reset-password/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', django.contrib.auth.views.password_reset_confirm),
    url(r'^accounts/reset-password/done/$', django.contrib.auth.views.password_reset_complete),

)