# -*- encoding: utf-8 -*-
#
# Copyright © 2015 Robert Weidlich. All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
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
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from django import forms
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.utils.translation import ugettext as _

from django_hosts.reverse import reverse_full
from guardian.mixins import PermissionRequiredMixin
from twython import Twython, TwythonError

from .forms import IRCWidget, IRCNETWORKS
from radioportal.models import PrimaryNotification, SecondaryNotification,\
    AuphonicAccount
from radioportal.models import TwitterAccount, IRCChannel, HTTPCallback
from radioportal.models import NotificationTemplate, Show
from django.forms.widgets import Select

from urllib import quote_plus
import requests

# Forms
class StartTemplateForm(forms.ModelForm):
    class Meta:
        model = NotificationTemplate
        fields = ('text',)
        labels = {
            'text': _("Template for start"),
        }


class StopTemplateForm(forms.ModelForm):
    class Meta:
        model = NotificationTemplate
        fields = ('text',)
        labels = {
            'text': _("Template for stop"),
        }


class RolloverTemplateForm(forms.ModelForm):
    class Meta:
        model = NotificationTemplate
        fields = ('text',)
        labels = {
            'text': _("Template for rollover"),
        }


class TwitterForm(forms.ModelForm):
    class Meta:
        model = TwitterAccount
        fields = ["screen_name", ]
        widgets = {
            'screen_name': forms.TextInput(attrs={'readonly': 'readonly'}),
        }


class IRCForm(forms.ModelForm):
    class Meta:
        model = IRCChannel
        widgets = {
            'url': IRCWidget(choices=IRCNETWORKS),
        }
        labels = {
            'url': _("IRC Network and Channel"),
        }


class HTTPForm(forms.ModelForm):
    class Meta:
        model = HTTPCallback

class AuphonicForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AuphonicForm, self).__init__(*args, **kwargs)
        url = "https://auphonic.com/api/presets.json"
        headers = {"Authorization": "Bearer %s" % self.instance.access_token}
        r = requests.get(url, headers=headers)
        ch = [(None, '----'),]
        if r.status_code == 200:
            res = r.json()
            for preset in res["data"]:
                ch.append((preset["uuid"], preset["preset_name"]))
        self.fields["preset"].choices = ch

    preset = forms.ChoiceField()

    class Meta:
        model = AuphonicAccount
        fields = ["username", "preset", "start_production"]
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
        labels = {
            'username': _("Auphonic Login Name"),
            'preset': _("Auphonic Preset"),
            'start_production': _("Start Production after upload")
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        model = PrimaryNotification
        exclude = ['show', 'path', 'start', 'stop', 'rollover', 'system']


class SecondaryNotificationForm(forms.ModelForm):
    class Meta:
        model = SecondaryNotification
        fields = ['primary', ]


# Generic Views
class MultipleFormMixin(object):
    aux_form_class = {}

    def get_aux_form_class(self, name):
        return self.aux_form_class[name]

    def form_valid(self, form, aux_forms):
        """
        Called if all forms are valid. redirects to a
        success page.
        """
        objs = [(name, f.save()) for name, f in aux_forms.iteritems()]
        self.objects = dict(objs)

        for name, obj in self.objects.iteritems():
            setattr(form.instance, name, obj)

        form.instance.show = Show.objects.get(slug=self.kwargs["slug"])
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, aux_forms):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, aux_forms=aux_forms))


class MultipleFormCreateView(MultipleFormMixin, CreateView):

    def get(self, request, *args, **kwargs):
        self.object = None
        klass = self.get_form_class()
        form = self.get_form(klass)
        aux_forms = {}
        for name in self.aux_form_class.keys():
            formklass = self.get_aux_form_class(name)
            aux_forms[name] = formklass(prefix=name)
        ctx = self.get_context_data(form=form, aux_forms=aux_forms)
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        self.object = None
        klass = self.get_form_class()
        form = self.get_form(klass)
        aux_forms = {}
        for name in self.aux_form_class.keys():
            formklass = self.get_aux_form_class(name)
            aux_forms[name] = formklass(request.POST, prefix=name)
        if form.is_valid() and all([f.is_valid() for f in aux_forms.values()]):
            return self.form_valid(form, aux_forms)
        else:
            return self.form_invalid(form, aux_forms)


class MultipleFormUpdateView(MultipleFormMixin, CreateView):

    pk_url_kwarg = 'nslug'

    def get_aux_object(self, name):
        return getattr(self.object, name)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        klass = self.get_form_class()
        form = self.get_form(klass)
        aux_forms = {}
        for name in self.aux_form_class.keys():
            formklass = self.get_aux_form_class(name)
            inst = self.get_aux_object(name)
            aux_forms[name] = formklass(prefix=name, instance=inst)
        ctx = self.get_context_data(form=form, aux_forms=aux_forms)
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        klass = self.get_form_class()
        form = self.get_form(klass)
        aux_forms = {}
        for name in self.aux_form_class.keys():
            formklass = self.get_aux_form_class(name)
            aux_forms[name] = formklass(request.POST, prefix=name,
                                        instance=self.get_aux_object(name))
        if form.is_valid() and all([f.is_valid() for f in aux_forms.values()]):
            return self.form_valid(form, aux_forms)
        else:
            return self.form_invalid(form, aux_forms)


# views
class NotificationMixin(PermissionRequiredMixin):
    permission_required = 'change_show'

    aux_form_class = {
        'path': {
            'twitter': TwitterForm,
            'irc': IRCForm,
            'http': HTTPForm,
            'auphonic': AuphonicForm,
        },
        'start': StartTemplateForm,
        'stop': StopTemplateForm,
        'rollover': RolloverTemplateForm,
    }

    def get_permission_object(self):
        return Show.objects.get(slug=self.kwargs["slug"])

    def get_aux_form_class(self, name):
        klass = super(NotificationMixin, self).get_aux_form_class(name)
        if name == "path":
            klass = klass[self.kwargs["path"]]
        return klass

    def get_aux_object(self, name):
        if name == "path":
            return self.object.path.get()
        return super(NotificationMixin, self).get_aux_object(name)

    def get_context_data(self, **ctx):
        ctx = super(MultipleFormMixin, self).get_context_data(**ctx)
        show = Show.objects.get(slug=self.kwargs["slug"])
        ctx["show"] = show
        ctx["path"] = self.kwargs["path"]
        ctx["primary"] = self.primary
        return ctx


class CreateNotificationView(NotificationMixin, MultipleFormCreateView):
    form_class = NotificationForm

    primary = True

    template_name = "radioportal/dashboard/notification/edit.html"

    def get_success_url(self):
        return reverse_full('dashboard', 'admin-show-notification',
                            view_kwargs={'slug': self.kwargs["slug"]})


class UpdateNotificationView(NotificationMixin, MultipleFormUpdateView):
    form_class = NotificationForm

    model = PrimaryNotification

    template_name = "radioportal/dashboard/notification/edit.html"

    primary = True

    def get_success_url(self):
        return reverse_full('dashboard', 'admin-show-notification',
                            view_kwargs={'slug': self.kwargs["slug"]})

    def get_permission_object(self):
        obj = self.get_object()
        if (hasattr(obj, "system") and
                (not obj.system or self.request.user.is_superuser)):
            return super(UpdateNotificationView, self).get_permission_object()


class UpdateSecondaryNotificationView(NotificationMixin,
                                      MultipleFormUpdateView):
    aux_form_class = {
        'path': {
            'twitter': TwitterForm,
            'irc': IRCForm,
            'http': HTTPForm,
        },
    }

    form_class = SecondaryNotificationForm

    model = SecondaryNotification

    template_name = "radioportal/dashboard/notification/edit.html"

    primary = False

    def get_form_class(self):
        form_class = super(UpdateSecondaryNotificationView,
                           self).get_form_class()
        show = self.get_permission_object()
        twa = TwitterAccount.objects.filter(
            notificationpath_ptr__primarynotification__show=show)
        qs = PrimaryNotification.objects.filter(path__in=twa)
        form_class.base_fields['primary'].queryset = qs
        return form_class

    def get_success_url(self):
        return reverse_full('dashboard', 'admin-show-notification',
                            view_kwargs={'slug': self.kwargs["slug"]})


class DeleteNotificationView(PermissionRequiredMixin, DeleteView):
    model = PrimaryNotification
    pk_url_kwarg = 'nslug'
    permission_required = 'change_show'
    template_name = "radioportal/dashboard/notification/delete.html"

    def get_permission_object(self):
        obj = self.get_object()
        if hasattr(obj, "system"):
            if obj.system and not self.request.user.is_superuser:
                return None
        return obj.show

    def get_success_url(self):
        return reverse_full('dashboard', 'admin-show-notification',
                            view_kwargs={'slug': self.kwargs["slug"]})

    def get_context_data(self, **ctx):
        ctx = super(DeleteNotificationView, self).get_context_data(**ctx)
        show = Show.objects.get(slug=self.kwargs["slug"])
        ctx["show"] = show
        return ctx


class DeleteSecondaryNotificationView(DeleteNotificationView):
    model = SecondaryNotification


class NotificationListView(PermissionRequiredMixin, ListView):
    model = PrimaryNotification

    permission_required = 'change_show'

    template_name = "radioportal/dashboard/notification/list.html"

    def get_permission_object(self):
        return Show.objects.get(slug=self.kwargs["slug"])

    def get_context_data(self, **ctx):
        ctx = super(NotificationListView, self).get_context_data(**ctx)
        show = Show.objects.get(slug=self.kwargs["slug"])
        ctx["show"] = show
        ctx["secondary"] = SecondaryNotification.objects.filter(
            show__slug=self.kwargs["slug"])
        return ctx

    def get_queryset(self):
        qs = super(NotificationListView, self).get_queryset()
        return qs.filter(show__slug=self.kwargs["slug"])


def twitter_gettoken(request, slug, path):
    """
        Request auth tokens from twitter and redirect user to confirm
        authorization. Solved with redirect to prevent timeout of tokens.
    """
    twitter = Twython(settings.TWITTER_CONSUMER_KEY,
                      settings.TWITTER_CONSUMER_SECRET)
    cb = reverse_full('dashboard', 'admin-show-notification-twitter-callback',
                      view_kwargs={'slug': slug, 'path': path})
    auth = twitter.get_authentication_tokens(callback_url=cb)
    request.session['twitter_%s_oauth_token' % path] = auth['oauth_token']
    request.session[
        'twitter_%s_oauth_token_secret' % path] = auth['oauth_token_secret']
    return redirect(auth['auth_url'])


def twitter_callback(request, slug, path):
    """
        User authorized us at twitter and got redirected with the
        necessary tokens. Obtain final tokens and create objects
        for storage
    """
    if not "oauth_verifier" in request.GET:
        url = reverse_full('dashboard', 'admin-show-notification',
                       view_kwargs={'slug': slug})
        return redirect(url)
    oauth_verifier = request.GET['oauth_verifier']
    twitter = Twython(settings.TWITTER_CONSUMER_KEY,
                      settings.TWITTER_CONSUMER_SECRET,
                      request.session['twitter_%s_oauth_token' % path],
                      request.session['twitter_%s_oauth_token_secret' % path])
    final_step = twitter.get_authorized_tokens(oauth_verifier)

    del request.session['twitter_%s_oauth_token' % path]
    del request.session['twitter_%s_oauth_token_secret' % path]

    show = Show.objects.get(slug=slug)
    if not request.user.has_perm('change_show', show):
        return HttpResponse('Unauthorized', status=401)

    twitter = Twython(settings.TWITTER_CONSUMER_KEY,
                      settings.TWITTER_CONSUMER_SECRET,
                      final_step['oauth_token'],
                      final_step['oauth_token_secret'])

    try:
        res = twitter.verify_credentials(skip_status=True)
    except TwythonError as e:
        return HttpResponse("Error occured during Twitter authorization: %s" %
                            e.msg)

    account = TwitterAccount(
        oauth_token=final_step['oauth_token'],
        oauth_secret=final_step['oauth_token_secret'],
        screen_name=res["screen_name"])
    account.save()

    if path == "primary":
        start = NotificationTemplate()
        start.save()
        stop = NotificationTemplate()
        stop.save()
        rollover = NotificationTemplate()
        rollover.save()
        noti = PrimaryNotification(path=account, start=start, stop=stop,
                                   rollover=rollover, show=show)
        noti.save()

        kwargs = {'slug': show.slug, "path": "twitter", "nslug": noti.id}
        url = reverse_full('dashboard', 'admin-show-notification-edit',
                           view_kwargs=kwargs)
    elif path == "secondary":
        noti = SecondaryNotification(show=show, path=account)
        noti.save()

        kwargs = {'slug': show.slug, "path": "twitter", "nslug": noti.id}
        url = reverse_full('dashboard',
                           'admin-show-secondary-notification-edit',
                           view_kwargs=kwargs)
    return redirect(url)


def auphonic_gettoken(request, slug):
    show = Show.objects.get(slug=slug)
    if not request.user.has_perm('change_show', show):
        return HttpResponse('Unauthorized', status=401)

    url = "https://auphonic.com/oauth2/authorize/?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    cb = reverse_full('dashboard', 'admin-show-notification-auphonic-callback', view_kwargs={'slug': slug})

    cb = quote_plus(cb)

    return redirect(url.format(client_id=settings.AUPHONIC_CLIENT_ID, redirect_uri=cb))

def auphonic_callback(request, slug):
    token = request.GET["code"]

    show = Show.objects.get(slug=slug)
    if not request.user.has_perm('change_show', show):
        return HttpResponse('Unauthorized', status=401)

    url = "https://auphonic.com/oauth2/token/"
    cb = reverse_full('dashboard', 'admin-show-notification-auphonic-callback', view_kwargs={'slug': slug})
    data = {
        'client_id': settings.AUPHONIC_CLIENT_ID,
        'client_secret': settings.AUPHONIC_CLIENT_SECRET,
        'redirect_uri': cb,
        'grant_type': "authorization_code",
        'code': token
    }

    r = requests.post(url, data=data)
    if r.status_code == 200:
        res = r.json()

        token = res["access_token"]

        url = "https://auphonic.com/api/user.json"
        headers = {"Authorization": "Bearer %s" % token}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            res = r.json()

            account, created = AuphonicAccount.objects.get_or_create(userid=res["data"]["user_id"], primarynotification__show__slug=slug)

            account.access_token = token
            account.username = res["data"]["username"]

            account.save()

            if created:
                start = NotificationTemplate()
                start.save()
                stop = NotificationTemplate()
                stop.save()
                rollover = NotificationTemplate()
                rollover.save()

                noti = PrimaryNotification(path=account, start=start, stop=stop,
                                           rollover=rollover, show=show)
                noti.save()

            kwargs = {'slug': slug, "path": "auphonic", "nslug": noti.id}

            url = reverse_full('dashboard', 'admin-show-notification-edit',
                               view_kwargs=kwargs)

    url = reverse_full('dashboard', 'admin-show-notification',
                       view_kwargs={'slug': slug})
    return redirect(url)
