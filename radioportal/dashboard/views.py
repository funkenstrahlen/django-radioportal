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
from django.db.models.aggregates import Max, Sum, Min
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
try:
    from django.utils.text import slugify
except ImportError:
    from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView, BaseUpdateView
from django.views.generic.list import ListView

from django_hosts.resolvers import reverse

from guardian.decorators import permission_required
from guardian.shortcuts import get_objects_for_user, assign

from radioportal import forms
from radioportal.dashboard import forms as dforms
from radioportal.dashboard.decorators import superuser_only
from radioportal.messages.send import send_msg
from radioportal.models import Show, Channel, Episode, PodcastFeed, EpisodePart, Marker, Message, SourcedStream

from django.core.mail import send_mail
from formtools.wizard.views import SessionWizardView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from django.conf import settings

import datetime
import requests
import simplejson
import urlparse as urllib_parse


@csrf_exempt
def icecast_source_auth(request):
    response = HttpResponse()
    for k in ("user", "pass", "mount", "server"):
        if not k in request.REQUEST:
            response["icecast-auth-message"] = "Parameter is missing"
            response.status_code = 400
            return response
    user = request.REQUEST["user"]
    passwd = request.REQUEST["pass"]
    mount = request.REQUEST["mount"]
    server = request.REQUEST["server"]

    if not server.endswith("xenim.de"):
        response["icecast-auth-message"] = "Server is not permitted to use this"
        response.status_code = 403
        return response
    print mount, user, passwd,
    stream = get_object_or_404(SourcedStream, mount=mount[1:])
    if stream.user == user and stream.password == passwd:
        response["icecast-auth-user"] = 1
        response["icecast-auth-timelimit"] = 10*60
        print "auth successfull"
    else:
        response["icecast-auth-message"] = "Username or password wrong"
        print "sth failed", repr(stream.user), repr(user), repr(stream.password), repr(passwd)
    return response

@csrf_exempt
def icecast_sandbox_lauth(request):
    response = HttpResponse()
    for k in ("mount", "server"):
        if not k in request.REQUEST:
            response["icecast-auth-message"] = "Parameter is missing"
            response.status_code = 400
            return response
    user = None
    passwd = None
    if "user" in request.REQUEST:
        user = request.REQUEST["user"]
    if "pass" in request.REQUEST:
        passwd = request.REQUEST["pass"]
    mount = request.REQUEST["mount"]
    server = request.REQUEST["server"]

    if not server.endswith("xenim.de"):
        response["icecast-auth-message"] = "Server is not permitted to use this"
        response.status_code = 403
        return response
    stream = get_object_or_404(SourcedStream, mount=mount[1:])
    if stream.user == user and stream.password == passwd:
        response["icecast-auth-user"] = 1
        response["icecast-auth-timelimit"] = 30*60
    else:
        response["icecast-auth-user"] = 1
        response["icecast-auth-timelimit"] = 3*60
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
        url = reverse('api_dispatch_detail', kwargs=kwargs, host="review")
        header = {'Authorization': 'ApiKey %s:%s' % (self.request.user.username, self.request.user.api_key.key)}
        r = requests.get(url,  params={'format':'json'}, headers=header, verify=False)
        if not r.status_code == 200:
            return
        return r.json()

    def get_form_initial(self, step):
        """ Affected by Django Bug #18026 """
        if not 'initial' in self.storage.extra_data:
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
            self.storage.extra_data['rt_id'] = application['rt_id']

        if int(step) in self.storage.extra_data['initial']:
            return self.storage.extra_data['initial'][int(step)]
        elif step in ('2', '3'):
            data = self.get_cleaned_data_for_step('1')
            if data:
                name = slugify(data['name']).replace("-","")
                if step == '2':
                    return {'cluster': name}
                else:
                    return {'mount': "%s.mp3" % name}

    def done(self, form_list, **kwargs):
        new_user = form_list[0].save(commit=False)
        new_username = ("%s%s" % (new_user.first_name, new_user.last_name)).lower()
        user_pw = None

        if User.objects.filter(username=new_username, email=new_user.email).exists():
            user = User.objects.get(username=new_username, email=new_user.email)
        else:
            user = new_user
            user_pw = User.objects.make_random_password()
            user.set_password(user_pw)
            user.username = new_username
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

        assign('radioportal.change_channel', user, channel)
        assign('radioportal.change_stream', user, channel)

        assign('radioportal.change_episodes', user, show)
        assign('radioportal.change_show', user, show)

        mail_data = {
            'username': user.username,
            'password': user_pw,
            'dashboard_url': reverse('dashboard', host='dashboard'),
            'wiki_url': reverse('landing', host='wiki'),
            'wiki_communication_url': reverse('wiki-category-page', kwargs={'category': 'project', 'page': 'communication'}, host='wiki'),
        }
        mail_text = render_to_string("radioportal/dashboard/usercreatedmail_user.txt", mail_data)
        mail_subject = _("[xenim] Neuer Nutzer erstellt")

        send_mail(mail_subject, mail_text, "noreply@streams.xenim.de", [user.email,])

        if 'rt_id' in self.storage.extra_data:

            mail_data_rt = {'username': user.username, 'showname': show.name, 'channel': channel.cluster, 'streamname': stream.mount}
            mail_text_rt = render_to_string("radioportal/dashboard/usercreatedmail_rt.txt", mail_data_rt)
            mail_subject_rt = _("[xsn #%i] Neuer Nutzer") % self.storage.extra_data['rt_id']
            send_mail(mail_subject_rt, mail_text_rt, "noreply@streams.xenim.de", ["info-comment@streams.xenim.de",])

        return HttpResponseRedirect(reverse('dashboard', host='dashboard'))

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
    form_class = dforms.PermissionForm
    template_name = "radioportal/dashboard/perm.html"

    def get_success_url(self):
        return reverse('admin-list-users', host='dashboard')
    
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
               'radioportal.change_channel', klass=Channel).values_list('id', flat=True)
        channel_q = Q(content_type__pk=channel_type.id, object_id__in=channel_ids)
        show_type = ContentType.objects.get_for_model(Show)
        show_ids = get_objects_for_user(self.request.user,
               'radioportal.change_show', klass=Show).values_list('id', flat=True)
        show_q = Q(content_type__pk=show_type.id, object_id__in=show_ids)
        return qs.filter(channel_q | show_q)


class UserGroupListView(ListView):
    context_object_name = 'users'
    model = User
    template_name = "radioportal/dashboard/user_list.html"
    
    def get_context_data(self, **kwargs):
        ctx = super(UserGroupListView, self).get_context_data(**kwargs)
        ctx['groups'] = Group.objects.all()
        return ctx

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(UserGroupListView, self).dispatch(*args, **kwargs)


class UserCreateView(CreateView):
    form_class = forms.UserForm
    model = User
    template_name = "radioportal/dashboard/user_edit.html"

    def get_success_url(self):
        return reverse('admin-user-edit', kwargs={'slug': self.object.username}, host="dashboard")

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(UserCreateView, self).dispatch(*args, **kwargs)


class UserEditView(UpdateView):
    form_class = forms.UserForm
    model = User
    slug_field = 'username'
    template_name = "radioportal/dashboard/user_edit.html"

    def get_success_url(self):
        return reverse( 'admin-user-edit', kwargs={'slug': self.object.username}, host="dashboard")

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(UserEditView, self).dispatch(*args, **kwargs)


class GroupCreateView(CreateView):
    form_class = forms.GroupForm
    model = Group
    template_name = "radioportal/dashboard/group_edit.html"

    def get_success_url(self):
        return reverse('admin-group-edit', kwargs={'slug':self.object.id}, host="dashboard")
    
    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(GroupCreateView, self).dispatch(*args, **kwargs)


class GroupEditView(UpdateView):
    form_class = forms.GroupForm
    model = Group
    slug_field = 'id'
    template_name = "radioportal/dashboard/group_edit.html"
    
    def get_success_url(self):
        return reverse('admin-group-edit', kwargs={'slug': self.object.id}, host='dashboard')

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
    form_class = dforms.ShowForm
    model = Show
    template_name = "radioportal/dashboard/show_edit.html"

    def get_success_url(self):
        return reverse('admin-episode-list', kwargs={'slug': self.object.slug}, host='dashboard')

    @method_decorator(permission_required('radioportal.add_show'))
    def dispatch(self, *args, **kwargs):
        return super(ShowCreateView, self).dispatch(*args, **kwargs)


class ShowEditView(UpdateView):
    form_class = dforms.ShowForm
    model = Show
    slug_field = 'slug'
    template_name = "radioportal/dashboard/show_edit.html"

    def get_success_url(self):
        return reverse('admin-episode-list', kwargs={'slug': self.object.slug}, host='dashboard')

    def get_form_class(self):
        try:
            feed = self.object.podcastfeed
            if feed.enabled:
                return dforms.ShowReducedForm
        except PodcastFeed.DoesNotExist:
            pass
        return dforms.ShowForm

    @method_decorator(permission_required('radioportal.change_show', (Show, 'slug', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(ShowEditView, self).dispatch(*args, **kwargs)


class ShowDeleteView(DeleteView):
    model = Show
    slug_field = 'slug'
    template_name = "radioportal/dashboard/show_delete.html"

    def get_success_url(self):
        return reverse('dashboard', host='dashboard')

    @method_decorator(permission_required('radioportal.delete_show', (Show, 'slug', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(ShowDeleteView, self).dispatch(*args, **kwargs)


class PodcastFeedEditView(UpdateView):
    form_class = dforms.PodcastFeedForm
    model = PodcastFeed
    slug_field = 'show__slug'
    template_name = "radioportal/dashboard/showfeed_edit.html"

    def get_success_url(self):
        return reverse('admin-episode-list', kwargs={'slug': self.object.show.slug}, host='dashboard')
    
#    def get(self, request, *args, **kwargs):
#        self.object = self.get_object(request=request)
#        return super(BaseUpdateView, self).get(request, *args, **kwargs)

#    def get_object(self, queryset=None, request=None):
#        """
#        Returns the object the view is displaying.
#
#        By default this requires `self.queryset` and a `pk` or `slug` argument
#        in the URLconf, but subclasses can override this to return any object.
#        """
#        # Use a custom queryset if provided; this is required for subclasses
#        # like DateDetailView
#        if queryset is None:
#            queryset = self.get_queryset()
#
#        # Next, try looking up by primary key.
#        pk = self.kwargs.get('pk', None)
#        slug = self.kwargs.get('slug', None)
#        if pk is not None:
#            queryset = queryset.filter(pk=pk)
#        # Next, try looking up by slug.
#        elif slug is not None:
#            slug_field = self.get_slug_field()
#            queryset = queryset.filter(**{slug_field: slug})
#        # If none of those are defined, it's an error.
#        else:
#            raise AttributeError(u"Generic detail view %s must be called with "
#                                 u"either an object pk or a slug."
#                                 % self.__class__.__name__)
#        try:
#            obj = queryset.get()
#        except ObjectDoesNotExist:
#            obj = PodcastFeed(show=Show.objects.get(slug=slug))
#            obj.save()
#        
#        if request is not None:
#            if not request.user.has_perm('radioportal.change_show', obj.show):
#                raise PermissionDenied()
#
#        return obj
    
    @method_decorator(permission_required('radioportal.change_show', (Show, 'slug', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(PodcastFeedEditView, self).dispatch(*args, **kwargs)
    

class EpisodeListView(ListView):
    model = Episode
    template_name = "radioportal/dashboard/episode_list.html"
    
    def get_queryset(self):
        qs = super(EpisodeListView, self).get_queryset()
        qs = qs.filter(show__slug=self.kwargs['slug'])
        qs = qs.order_by('-slug')
        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super(EpisodeListView, self).get_context_data(**kwargs)
        ctx['show'] = Show.objects.get(slug=self.kwargs['slug'])
        return ctx
    
    @method_decorator(permission_required('radioportal.change_show', (Show, 'slug', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeListView, self).dispatch(*args, **kwargs)

class EpisodeCreateView(CreateView):
    form_class = dforms.CreateEpisodeForm
    model = Episode # FIXME: form uses EpisodePart as Model
    template_name = "radioportal/dashboard/episode_create.html"

    def get_success_url(self):
        return reverse('admin-episodepart-edit', kwargs={'pk': self.object.id}, host='dashboard')

    def get_initial(self):
        s = Show.objects.get(slug=self.kwargs['slug'])
        initial = super(EpisodeCreateView, self).get_initial()
        initial['show'] = s.id
        initial['slug'] = "%s%03i" % (s.defaultShortName, s.nextEpisodeNumber)
        return initial

    def get_form_class(self):
        form_class = super(EpisodeCreateView, self).get_form_class()
#        qs = get_objects_for_user(self.request.user, "radioportal.change_episodes", Show)
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

    @method_decorator(permission_required('radioportal.change_episodes', (Show, 'slug', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeCreateView, self).dispatch(*args, **kwargs)


class EpisodeEditView(UpdateView):
    form_class = dforms.EpisodeForm
    model = Episode
    template_name = "radioportal/dashboard/episode_edit.html"

    def get_success_url(self):
        return reverse('admin-episode-edit', kwargs={'pk': self.object.id}, host='dashboard')

    def get_context_data(self, **kwargs):
        ctx = super(EpisodeEditView, self).get_context_data(**kwargs)
        ctx['show'] = self.object.show
        return ctx

    @method_decorator(permission_required('radioportal.change_episodes', (Show, 'episode__pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeEditView, self).dispatch(*args, **kwargs)


class EpisodeDeleteView(DeleteView):
    model = Episode
    template_name = "radioportal/dashboard/episode_delete.html"

    def get_success_url(self):
        return reverse('admin-episode-list', kwargs={'slug': self.object.show.slug}, host='dashboard')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, "channel"):
            return HttpResponse("Currently Running Episodes cannot be deleted")
        return super(EpisodeDeleteView, self).delete(request, *args, **kwargs)

    @method_decorator(permission_required('radioportal.change_episodes', (Show, 'episode__pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeDeleteView, self).dispatch(*args, **kwargs)


class EpisodePartEditView(UpdateView):
    form_class = dforms.EpisodePartForm
    model = EpisodePart
    template_name = "radioportal/dashboard/episodepart_edit.html"

    def get_success_url(self):
        return reverse('admin-episodepart-edit', kwargs={'pk': self.object.id}, host='dashboard')

    def get_context_data(self, **kwargs):
        ctx = super(EpisodePartEditView, self).get_context_data(**kwargs)
        ctx['show'] = self.object.episode.show
        return ctx

    @method_decorator(permission_required('radioportal.change_episodes', (Show, 'episode__parts__pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodePartEditView, self).dispatch(*args, **kwargs)


class ChannelCreateView(CreateView):
    form_class = dforms.ChannelPlainCompoundForm
    model = Channel
    template_name = "radioportal/dashboard/channel_edit.html"

    def get_success_url(self):
        return reverse('admin-channel-edit', kwargs={'pk': self.object.id}, host='dashboard')

    def get_form_class(self):
        form_class = super(ChannelCreateView, self).get_form_class()
        qs = get_objects_for_user(self.request.user, "radioportal.change_show", Show)
        form_class.form_classes[0].base_fields['show'].queryset = qs
        return form_class

    @method_decorator(permission_required('radioportal.add_channel'))
    def dispatch(self, *args, **kwargs):
        return super(ChannelCreateView, self).dispatch(*args, **kwargs)


class ChannelChangeCurrentEpisode(UpdateView):
    form_class = dforms.ChannelChangeEpisodeForm
    model = Channel
    template_name = "radioportal/dashboard/channel_change_c_episode.html"

    def get_success_url(self):
        return reverse('admin-channel-edit', kwargs={'pk': self.object.id}, host='dashboard')

    def form_valid(self, form):
        ch = Channel.objects.get(pk=self.kwargs['pk'])
        move = form.cleaned_data['move_part']

        old_episode = ch.currentEpisode
        part = old_episode.current_part
        new_episode = form.cleaned_data['currentEpisode']

        if move:
            part.episode = new_episode
            part.save()
    
            new_episode.current_part = part
            new_episode.status = Episode.STATUS[1][0]
            new_episode.save()
        else:
            part.end = datetime.datetime.now()
            part.save()


            part = new_episode.parts.all().reverse()[0]
            part.begin = datetime.datetime.now()
            part.save()

            new_episode.current_part = part
            new_episode.status = Episode.STATUS[1][0]
            new_episode.save()

        old_episode.status = Episode.STATUS[0][0]
        old_episode.current_part = None
        old_episode.save()

        data = {
            'channel': ch.cluster,
            'episode': new_episode.get_id(),
            'old': { 'episode': old_episode.get_id() },
        }

        if form.cleaned_data['notify']:
            data['publish'] = {
                'twitter': new_episode.show.twitter,
                'chat': new_episode.show.chat,
            }

        send_msg("channel.update", simplejson.dumps(data), "backenddata")

        return super(ChannelChangeCurrentEpisode, self).form_valid(form)

    def get_form_class(self):
        form_class = super(ChannelChangeCurrentEpisode, self).get_form_class()
        show_qs = get_objects_for_user(self.request.user, "radioportal.change_show", Show)
        show_qs = show_qs.filter(channel__in=(self.object,))
        qs = Episode.objects.filter(show__in=show_qs).annotate(begin=Min('parts__begin')).order_by('-begin')
        form_class.base_fields['currentEpisode'].queryset = qs
        return form_class

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.currentEpisode:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)
        else:
            return super(ChannelChangeCurrentEpisode, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.currentEpisode:
            return self.get(request, *args, **kwargs)
        else:
            return super(ChannelChangeCurrentEpisode, self).post(request, *args, **kwargs)

    @method_decorator(permission_required('radioportal.change_channel', (Channel, 'pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(ChannelChangeCurrentEpisode, self).dispatch(*args, **kwargs)


class ChannelEditView(UpdateView):
    form_class = dforms.ChannelCompoundForm
    model = Channel
    template_name = "radioportal/dashboard/channel_edit.html"

    def get_success_url(self):
        return reverse('admin-channel-edit', kwargs={'pk': self.object.id}, host='dashboard')

    def get_form_class(self):
        form_class = super(ChannelEditView, self).get_form_class()
        qs = get_objects_for_user(self.request.user, "radioportal.change_show", Show)
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

    @method_decorator(permission_required('radioportal.change_channel', (Channel, 'pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(ChannelEditView, self).dispatch(*args, **kwargs)


class ChannelClusterEditView(ChannelEditView):
    slug_field = "cluster"

    def get_object(self):
        return Channel.objects.get(cluster=self.kwargs.get("slug"))

    @method_decorator(permission_required('radioportal.change_channel', (Channel, 'cluster', 'slug'), return_403=True))
    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)


class ChannelDeleteView(DeleteView):
    model = Channel
    template_name = "radioportal/dashboard/channel_delete.html"

    def get_success_url(self):
        return reverse('dashboard', host='dashboard')

    @method_decorator(permission_required('radioportal.delete_channel', (Channel, 'pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(ChannelDeleteView, self).dispatch(*args, **kwargs)


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
