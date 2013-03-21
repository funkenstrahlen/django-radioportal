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
Created on 28.05.2011

@author: robert
'''

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Q, signals
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
try:
    from django.utils.text import slugify
except ImportError:
    from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView, BaseUpdateView
from django.views.generic.list import ListView

from django_hosts.reverse import reverse_full

from guardian.decorators import permission_required
from guardian.shortcuts import get_objects_for_user, assign

from radioportal import forms
from radioportal.dashboard import forms as dforms
from radioportal.dashboard.decorators import superuser_only
from radioportal.models import Show, Channel, Episode, ShowFeed, EpisodePart, Marker, Message, AgbAcception

from django.core.mail import send_mail
from django.contrib.formtools.wizard.views import SessionWizardView
from django.views.decorators.csrf import csrf_exempt

import datetime
import requests

@csrf_exempt
def icecast_source_auth(request):
    response = HttpResponse()
    for k in ("user", "pass", "mount", "server"):
        if not k in request.REQUEST:
            response.status_code = 400
            return response
    user = request.REQUEST["user"]
    passwd = request.REQUEST["pass"]
    mount = request.REQUEST["mount"]
    server = request.REQEST["server"]

    if not server.endswith("xenim.de"):
        response.status_code = 403
        return response
    stream = SourcedStream.objects.get(mount=mount[1:])
    if stream.user == user and stream.password == passwd:
        response["icecast-auth-user"] = 1
    return response

class UserChannelStreamAddView(SessionWizardView):
    template_name = "radioportal/dashboard/create_wizard.html"
    forms_for_context = False
    initial_error = None

    def fetch_initial(self):
        id = self.kwargs.get('id', None)
        if not id:
            return
        kwargs = {'api_name': 'v1', 'resource_name': 'application', 'pk': id}
        url = "http:%s" % reverse_full('review', 'api_dispatch_detail', view_kwargs=kwargs)
        header = {'Authorization': 'ApiKey %s:%s' % (self.request.user.username, self.request.user.api_key.key)}
        r = requests.get(url,  params={'format':'json'}, headers=header)
        if not r.status_code == 200:
            return
        return r.json()

    def get_form_initial(self, step):
        """ Affected by Django Bug #18026 """
        if not "initial" in self.storage.extra_data:
            application = self.fetch_initial()

            if not application:
                self.initial_error = _("Could not fetch matching application")
                self.storage.extra_data['initial'] = {}
                return {}
            elif not application['status'] == "2_ACCEPTED":
                self.initial_error = _("Application is in wrong state. Ignoring it.")
                self.storage.extra_data['initial'] = {}
                return {}
            
            initial = {}

            initial[0] = {}
            name = application['contact_name']
            if " " in name:
                initial[0]['first_name'], initial[0]['last_name'] = name.split(" ", 1)
            else:
                initial[0]['first_name'] = name
                initial[0]['last_name'] = ""
            initial[0]['email'] = application['contact_email']
            
            initial[1] = {}
            initial[1]['name'] = application['name']
            initial[1]['url'] = application['homepage']

            self.storage.extra_data['initial'] = initial
        if int(step) in self.storage.extra_data['initial']:
            return self.storage.extra_data['initial'][int(step)]
        elif step in ('2', '3'):
            data = self.get_cleaned_data_for_step('1')
            print data
            if data:
                name = slugify(data['name']).replace("-","")
                if step == '2':
                    return {'cluster': name}
                else:
                    return {'mount': "%s.mp3" % name}

    def done(self, form_list, **kwargs):
        user_pw = User.objects.make_random_password()
        user = form_list[0].save(commit=False)
        user.set_password(user_pw)
        user.username = ("%s%s" % (user.first_name, user.last_name)).lower()
        user.save()

        show = form_list[1].save()
        
        channel = form_list[2].save(commit=False)
        channel.mapping_method = '["find-from-title","make-from-title","find-or-make-live"]'
        channel.save()
        channel.show.add(show)

        stream = form_list[3].save(commit=False)
        stream.user = "source"
        stream_pw = User.objects.make_random_password()
        stream.password = stream_pw
        stream.channel = channel
        stream.save()

        assign('change_channel', user, channel)
        assign('change_stream', user, channel)

        assign('change_episodes', user, show)
        assign('change_show', user, show)

        mail_data = {'username': user.username, 'password': user_pw}
        mail_text = _("USERCREATEDMAIL with %(username)s %(password)s" % mail_data)
        mail_subject = _("[xenim] Neuer Nutzer erstellt")
        send_mail(mail_subject, mail_text, "noreply@streams.xenim.de", [user.email,])

        return HttpResponseRedirect(reverse_full('dashboard', 'dashboard'))

    def get_form_kwargs(self, step=None):
        kwargs = super(UserChannelStreamAddView, self).get_form_kwargs(step)
        if self.forms_for_context and step and step != self.steps.current:
            kwargs['disabled'] = 'disabled'
        return kwargs

    def get_context_data(self, form, **kwargs):
        ctx = super(UserChannelStreamAddView, self).get_context_data(form, **kwargs)
        form_list = self.get_form_list()
        wizard_forms = {}
        self.forms_for_context = True
        for step in form_list.keys():
            if step != self.steps.current:
                form = self.get_form(
                      step=step,
                      data=self.storage.get_step_data(step))
            else:
                form = None
            wizard_forms[int(step)+1] = form
            ctx['wizard_forms'] = wizard_forms
        self.forms_for_context = False
        ctx['initial_error'] = self.initial_error
        return ctx

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(UserChannelStreamAddView, self).dispatch(*args, **kwargs)

class PermissionChangeView(FormView):
    template_name = "radioportal/dashboard/perm.html"
    
    form_class = dforms.PermissionForm
    
    success_url = '/dashboard/user/'
    
    def get_form_kwargs(self):
        kwargs = super(PermissionChangeView, self).get_form_kwargs()
        kwargs['user'] = User.objects.get(username=self.kwargs['user_name'])
        kwargs['model'] = ContentType.objects.get(model=self.kwargs['model']).model_class()
        return kwargs
       
    def get_context_data(self, **kwargs):
        ctx = super(PermissionChangeView, self).get_context_data(**kwargs)
        ctx['editeduser'] = User.objects.get(username=self.kwargs['user_name'])
        ctx['model'] = ContentType.objects.get(model=self.kwargs['model']).model_class()._meta.object_name
        return ctx

    
    def form_valid(self, form):
        form.save_obj_perms()
        return super(PermissionChangeView, self).form_valid(form)
    
    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(PermissionChangeView, self).dispatch(*args, **kwargs)


class MessageListView(ListView):
    template_name = "radioportal/dashboard/message_list.html"
    model = Message
    context_object_name = "xsn_msgs"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MessageListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = super(MessageListView, self).get_queryset()
        channel_type = ContentType.objects.get_for_model(Channel)
        channel_ids = get_objects_for_user(self.request.user, 
               'change_channel', klass=Channel).values_list('id', flat=True)
        channel_q = Q(content_type__pk=channel_type.id, object_id__in=channel_ids)
        show_type = ContentType.objects.get_for_model(Show)
        show_ids = get_objects_for_user(self.request.user,
               'change_show', klass=Show).values_list('id', flat=True)
        show_q = Q(content_type__pk=show_type.id, object_id__in=show_ids)
        return qs.filter(channel_q | show_q)


class UserGroupListView(ListView):
    template_name = "radioportal/dashboard/user_list.html"
    model = User
    context_object_name = 'users'
    
    def get_context_data(self, **kwargs):
        ctx = super(UserGroupListView, self).get_context_data(**kwargs)
        ctx['groups'] = Group.objects.all()
        return ctx

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(UserGroupListView, self).dispatch(*args, **kwargs)


class UserCreateView(CreateView):
    template_name = "radioportal/dashboard/user_edit.html"
    model = User
    form_class = forms.UserForm
    success_url = '/dashboard/user/%(username)s/'

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(UserCreateView, self).dispatch(*args, **kwargs)


class UserEditView(UpdateView):
    template_name = "radioportal/dashboard/user_edit.html"
    model = User
    slug_field = 'username'
    form_class = forms.UserForm
    success_url = '/dashboard/user/%(username)s/'

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(UserEditView, self).dispatch(*args, **kwargs)


class GroupCreateView(CreateView):
    template_name = "radioportal/dashboard/group_edit.html"
    model = Group
    success_url = '/dashboard/group/%(id)s/'
    form_class = forms.GroupForm
    
    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(GroupCreateView, self).dispatch(*args, **kwargs)


class GroupEditView(UpdateView):
    template_name = "radioportal/dashboard/group_edit.html"
    model = Group
    slug_field = 'id'
    success_url = '/dashboard/group/%(id)s/'
    form_class = forms.GroupForm
    
    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(GroupEditView, self).dispatch(*args, **kwargs)


class LandingView(TemplateResponseMixin, View):
    template_name = "radioportal/dashboard/landing.html" 

    def get(self, request, *args, **kwargs):
        ctx = {}
        ctx['shows'] = get_objects_for_user(request.user, 'radioportal.change_show', Show).extra(
			select={'lower_name': 'lower(name)'}).order_by('lower_name')
        ctx['channels'] = get_objects_for_user(request.user, 'radioportal.change_channel').order_by('cluster')
        return self.render_to_response(ctx)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LandingView, self).dispatch(*args, **kwargs)


class ShowCreateView(CreateView):
    template_name = "radioportal/dashboard/show_edit.html"
    success_url = '/dashboard/show/%(slug)s/'
    form_class = dforms.ShowForm
    model = Show

    @method_decorator(permission_required('add_show'))
    def dispatch(self, *args, **kwargs):
        return super(ShowCreateView, self).dispatch(*args, **kwargs)


class ShowEditView(UpdateView):
    template_name = "radioportal/dashboard/show_edit.html"
    success_url = '/dashboard/show/%(slug)s/'
    form_class = dforms.ShowForm
    slug_field = 'slug'
    model = Show

    def get_form_class(self):
        try:
            feed = self.object.showfeed
            if feed.enabled:
                return dforms.ShowReducedForm
        except ShowFeed.DoesNotExist:
            pass
        return dforms.ShowForm

    @method_decorator(permission_required('change_show', (Show, 'slug', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(ShowEditView, self).dispatch(*args, **kwargs)

class ShowDeleteView(DeleteView):
    template_name = "radioportal/dashboard/show_delete.html"
    success_url = "/dashboard/"
    slug_field = 'slug'
    model = Show

    @method_decorator(permission_required('delete_show', (Show, 'slug', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(ShowDeleteView, self).dispatch(*args, **kwargs)

class ShowFeedEditView(UpdateView):
    template_name = "radioportal/dashboard/showfeed_edit.html"
    success_url = '/dashboard/show/%(slug)s/'
    slug_field = 'show__slug'
    model = ShowFeed
    form_class = dforms.ShowFeedForm
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object(request=request)
        return super(BaseUpdateView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None, request=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get('pk', None)
        slug = self.kwargs.get('slug', None)
        if pk is not None:
            queryset = queryset.filter(pk=pk)
        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})
        # If none of those are defined, it's an error.
        else:
            raise AttributeError(u"Generic detail view %s must be called with "
                                 u"either an object pk or a slug."
                                 % self.__class__.__name__)
        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            obj = ShowFeed(show=Show.objects.get(slug=slug))
            obj.save()
        
        if request is not None:
            if not request.user.has_perm('change_show', obj.show):
                raise PermissionDenied()

        return obj
    
    def get_success_url(self):
        return self.success_url % self.object.show.__dict__
    
    @method_decorator(permission_required('change_show', (Show, 'slug', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(ShowFeedEditView, self).dispatch(*args, **kwargs)
    

class EpisodeListView(ListView):
    template_name = "radioportal/dashboard/episode_list.html"
    model = Episode
    
    def get_queryset(self):
        qs = super(EpisodeListView, self).get_queryset()
        qs = qs.filter(show__slug=self.kwargs['slug'])
        qs = qs.order_by('-slug')
        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super(EpisodeListView, self).get_context_data(**kwargs)
        ctx['show'] = Show.objects.get(slug=self.kwargs['slug'])
        return ctx
    
    @method_decorator(permission_required('change_show', (Show, 'slug', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeListView, self).dispatch(*args, **kwargs)

class EpisodeCreateView(CreateView):
    template_name = "radioportal/dashboard/episode_create.html"
    success_url = '/dashboard/episodepart/%(id)s/'
    form_class = dforms.CreateEpisodeForm
    model = Episode

    def get_initial(self):
        s = Show.objects.get(slug=self.kwargs['slug'])
        initial = super(EpisodeCreateView, self).get_initial()
        initial['show'] = s.id
        initial['slug'] = "%s%03i" % (s.defaultShortName, s.nextEpisodeNumber)
        return initial

    def get_form_class(self):
        form_class = super(EpisodeCreateView, self).get_form_class()
#        qs = get_objects_for_user(self.request.user, "change_episodes", Show)
#        form_class.base_fields['show'].queryset = qs
        return form_class

    def get_context_data(self, **kwargs):
        ctx = super(EpisodeCreateView, self).get_context_data(**kwargs)
        ctx['show'] = Show.objects.get(slug=self.kwargs['slug'])
        return ctx

    def form_valid(self, form):
        s = Show.objects.get(slug=self.kwargs['slug'])
        if form.instance.episode_id is None:
            qs = Episode.objects.filter(slug=form.cleaned_data['slug'], show=s)
            if qs.count() > 0:
                msg = u"An episode with this slug already exists in this show"
                form._errors["slug"] = form.error_class([msg])
                return super(EpisodeCreateView, self).form_invalid(form)
            e = Episode(slug=form.cleaned_data['slug'], show=s)
            e.save()
            s.nextEpisodeNumber+=1
            s.save()
            form.instance.episode = e
        return super(EpisodeCreateView, self).form_valid(form)

    @method_decorator(permission_required('change_episodes', (Show, 'slug', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeCreateView, self).dispatch(*args, **kwargs)


class EpisodeEditView(UpdateView):
    template_name = "radioportal/dashboard/episode_edit.html"
    success_url = '/dashboard/episode/%(id)s/'
    form_class = dforms.EpisodeForm
    model = Episode

    def get_context_data(self, **kwargs):
        ctx = super(EpisodeEditView, self).get_context_data(**kwargs)
        ctx['show'] = self.object.show
        return ctx

    @method_decorator(permission_required('change_episodes', (Show, 'episode__pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeEditView, self).dispatch(*args, **kwargs)

class EpisodeDeleteView(DeleteView):
    template_name = "radioportal/dashboard/episode_delete.html"
    model = Episode

    def get_success_url(self):
        return "/dashboard/show/%s/" % self.object.show.slug

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, "channel"):
            return HttpResponse("Currently Running Episodes cannot be deleted")
        return super(EpisodeDeleteView, self).delete(request, *args, **kwargs)

    @method_decorator(permission_required('change_episodes', (Show, 'episode__pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeDeleteView, self).dispatch(*args, **kwargs)


class EpisodePartEditView(UpdateView):
    template_name = "radioportal/dashboard/episodepart_edit.html"
    success_url = '/dashboard/episodepart/%(id)s/'
    form_class = dforms.EpisodePartForm
    model = EpisodePart

    def get_context_data(self, **kwargs):
        ctx = super(EpisodePartEditView, self).get_context_data(**kwargs)
        ctx['show'] = self.object.episode.show
        return ctx

    @method_decorator(permission_required('change_episodes', (Show, 'episode__parts__pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodePartEditView, self).dispatch(*args, **kwargs)


class ChannelCreateView(CreateView):
    template_name = "radioportal/dashboard/channel_edit.html"
    success_url = '/dashboard/channel/%(id)s/'
    form_class = dforms.ChannelPlainCompoundForm
    model = Channel

    def get_form_class(self):
        form_class = super(ChannelCreateView, self).get_form_class()
        qs = get_objects_for_user(self.request.user, "change_show", Show)
        form_class.form_classes[0].base_fields['show'].queryset = qs
        return form_class

    @method_decorator(permission_required('add_channel'))
    def dispatch(self, *args, **kwargs):
        return super(ChannelCreateView, self).dispatch(*args, **kwargs)


class ChannelEditView(UpdateView):
    template_name = "radioportal/dashboard/channel_edit.html"
    success_url = '/dashboard/channel/%(id)s/'
    form_class = dforms.ChannelCompoundForm
    model = Channel

    def get_form_class(self):
        form_class = super(ChannelEditView, self).get_form_class()
        qs = get_objects_for_user(self.request.user, "change_show", Show)
        form_class.form_classes[0].base_fields['show'].queryset = qs
        return form_class

    def get_context_data(self, **kwargs):
        ctx = super(ChannelEditView, self).get_context_data(**kwargs)
        ctx['show'] = self.object.show
        return ctx

    def get_form_kwargs(self):
        kwargs = super(ChannelEditView, self).get_form_kwargs()
        if self.request.user.has_perm('radioportal.add_stream', self.object):
            kwargs['extra'] = 1
        else:
            kwargs['extra'] = 0
        kwargs['can_delete'] = self.request.user.has_perm('radioportal.delete_stream', self.object)
        return kwargs

    @method_decorator(permission_required('change_channel', (Channel, 'pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(ChannelEditView, self).dispatch(*args, **kwargs)

class ChannelClusterEditView(ChannelEditView):
    slug_field = "cluster"

    def get_object(self):
        return Channel.objects.get(cluster=self.kwargs.get("slug"))

    @method_decorator(permission_required('change_channel', (Channel, 'cluster', 'slug'), return_403=True))
    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)


class ChannelDeleteView(DeleteView):
    template_name = "radioportal/dashboard/channel_delete.html"
    success_url = "/dashboard/"
    model = Channel

    @method_decorator(permission_required('delete_channel', (Channel, 'pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(ChannelDeleteView, self).dispatch(*args, **kwargs)


import urlparse as urllib_parse
from django.conf import settings

def is_safe_url(url, host=None):
    """
    Return ``True`` if the url is a safe redirection (i.e. it doesn't point to
    a different host).
    
    Always returns ``False`` on an empty url.
    """
    print "in modified is_safe_url"
    if not url:
        return False
    netloc = urllib_parse.urlparse(url)[1]
    return not netloc or netloc == host or netloc in settings.LOGIN_REDIRECT_WHITELIST

# class MarkerListView(ListView):
#     model = Marker
# 
#     template_name = "radioportal/dashboard/marker_list.html"
# 
#     def get_queryset(self):
#         self.episodepart = get_object_or_404(EpisodePart, id=self.args[0])
#         return Marker.objects.filter(episode=self.episodepart)
# 
# class MarkerCreateView(CreateView):
#     model = Marker
