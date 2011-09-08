'''
Created on 28.05.2011

@author: robert
'''
from django.views.generic.list import ListView
from django.contrib.auth.models import User, Group
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from radioportal import forms
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin, View
from radioportal.models import Show, StreamSetup, Episode, ShowFeed
from guardian.shortcuts import get_objects_for_user
from guardian.decorators import permission_required
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

class UserGroupListView(ListView):
    template_name = "radioportal/dashboard/user_list.html"
    model = User
    context_object_name = 'users'
    
    def get_context_data(self, **kwargs):
        ctx = super(UserGroupListView, self).get_context_data(**kwargs)
        ctx['groups'] = Group.objects.all()
        return ctx


class UserCreateView(CreateView):
    template_name = "radioportal/dashboard/user_edit.html"
    model = User
    form_class = forms.UserForm
    success_url = '/dashboard/user/%(username)s/'

    @method_decorator(permission_required('add_user'))
    def dispatch(self, *args, **kwargs):
        return super(UserCreateView, self).dispatch(*args, **kwargs)


class UserEditView(UpdateView):
    template_name = "radioportal/dashboard/user_edit.html"
    model = User
    slug_field = 'username'
    form_class = forms.UserForm
    success_url = '/dashboard/user/%(username)s/'

    @method_decorator(permission_required('add_user'))
    def dispatch(self, *args, **kwargs):
        return super(UserEditView, self).dispatch(*args, **kwargs)


class GroupCreateView(CreateView):
    template_name = "radioportal/dashboard/group_edit.html"
    model = Group
    success_url = '/dashboard/group/%(id)s/'
    form_class = forms.GroupForm
    
    @method_decorator(permission_required('add_group'))
    def dispatch(self, *args, **kwargs):
        return super(GroupCreateView, self).dispatch(*args, **kwargs)


class GroupEditView(UpdateView):
    template_name = "radioportal/dashboard/group_edit.html"
    model = Group
    slug_field = 'id'
    success_url = '/dashboard/group/%(id)s/'
    form_class = forms.GroupForm
    
    @method_decorator(permission_required('add_group'))
    def dispatch(self, *args, **kwargs):
        return super(GroupEditView, self).dispatch(*args, **kwargs)


class LandingView(TemplateResponseMixin, View):
    template_name = "radioportal/dashboard/landing.html" 

    def get(self, request, *args, **kwargs):
        ctx = {}
        ctx['shows'] = get_objects_for_user(request.user, 'change_show', Show).extra(
			select={'lower_name': 'lower(name)'}).order_by('lower_name')
        ctx['setups'] = get_objects_for_user(request.user, 'change_streamsetup', StreamSetup).order_by('cluster')
        return self.render_to_response(ctx)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LandingView, self).dispatch(*args, **kwargs)


class ShowCreateView(CreateView):
    template_name = "radioportal/dashboard/show_edit.html"
    success_url = '/dashboard/show/%(slugName)s/'
    form_class = forms.ShowForm
    model = Show

    @method_decorator(permission_required('add_show'))
    def dispatch(self, *args, **kwargs):
        return super(ShowCreateView, self).dispatch(*args, **kwargs)


class ShowEditView(UpdateView):
    template_name = "radioportal/dashboard/show_edit.html"
    success_url = '/dashboard/show/%(slugName)s/'
    #form_class = forms.ShowCompoundForm
    slug_field = 'slugName'
    model = Show

    @method_decorator(permission_required('change_show', (Show, 'slugName', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(ShowEditView, self).dispatch(*args, **kwargs)

class ShowDeleteView(DeleteView):
    template_name = "radioportal/dashboard/show_delete.html"
    success_url = "/dashboard/"
    slug_field = 'slugName'
    model = Show

    @method_decorator(permission_required('delete_show', (Show, 'slugName', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(ShowDeleteView, self).dispatch(*args, **kwargs)

class ShowFeedEditView(UpdateView):
    template_name = "radioportal/dashboard/showfeed_edit.html"
    success_url = '/dashboard/show/%(slugName)s/'
    slug_field = 'show__slugName'
    model = ShowFeed
    form_class = forms.ShowFeedForm
    
    def get_object(self, queryset=None):
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
            obj = ShowFeed(show=Show.objects.get(slugName=slug))
        return obj
    
    def get_success_url(self):
        return self.success_url % self.object.show.__dict__
    
    @method_decorator(permission_required('change_show', (Show, 'slugName', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(ShowFeedEditView, self).dispatch(*args, **kwargs)
    

class EpisodeListView(ListView):
    template_name = "radioportal/dashboard/episode_list.html"
    model = Episode
    
    def get_queryset(self):
        qs = super(EpisodeListView, self).get_queryset()
        qs = qs.filter(show__slugName=self.kwargs['slug'])
        qs = qs.order_by('-shortName')
        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super(EpisodeListView, self).get_context_data(**kwargs)
        ctx['show'] = Show.objects.get(slugName=self.kwargs['slug'])
        return ctx
    
    @method_decorator(permission_required('change_show', (Show, 'slugName', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeListView, self).dispatch(*args, **kwargs)

class EpisodeCreateView(CreateView):
    template_name = "radioportal/dashboard/episode_edit.html"
    success_url = '/dashboard/episode/%(id)s/'
    form_class = forms.CreateEpisodeForm
    model = Episode

    def get_initial(self):
        s = Show.objects.get(slugName=self.kwargs['slug'])
        initial = super(EpisodeCreateView, self).get_initial()
        initial['show'] = s.id
        initial['shortName'] = "%s%03i" % (s.shortName.lower(), s.nextEpisodeNumber)
        return initial

    def get_form_class(self):
        form_class = super(EpisodeCreateView, self).get_form_class()
        qs = get_objects_for_user(self.request.user, "change_episodes", Show)
        form_class.base_fields['show'].queryset = qs
        return form_class

    def get_context_data(self, **kwargs):
        ctx = super(EpisodeCreateView, self).get_context_data(**kwargs)
        ctx['show'] = Show.objects.get(slugName=self.kwargs['slug'])
        return ctx

    def form_valid(self, form):
        s = Show.objects.get(slugName=self.kwargs['slug'])
        s.nextEpisodeNumber+=1
        s.save()
        return super(EpisodeCreateView, self).form_valid(form)

    @method_decorator(permission_required('change_episodes', (Show, 'slugName', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeCreateView, self).dispatch(*args, **kwargs)


class EpisodeEditView(UpdateView):
    template_name = "radioportal/dashboard/episode_edit.html"
    success_url = '/dashboard/episode/%(id)s/'
    form_class = forms.EpisodeCompoundForm
    model = Episode

    def get_context_data(self, **kwargs):
        ctx = super(EpisodeEditView, self).get_context_data(**kwargs)
        ctx['show'] = self.object.show
        return ctx

    #FIXME
    #@method_decorator(permission_required('change_episodes', (Show, 'slugName', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeEditView, self).dispatch(*args, **kwargs)

class EpisodeDeleteView(DeleteView):
    template_name = "radioportal/dashboard/episode_delete.html"
    success_url = "/dashboard/"
    model = Episode

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, "streamsetup"):
            return HttpResponse("Currently Running Episodes cannot be deleted")
        return super(EpisodeDeleteView, self).delete(request, *args, **kwargs)

    #FIXME
    #@method_decorator(permission_required('change_episodes', (Show, 'slugName', 'slug')))
    def dispatch(self, *args, **kwargs):
        return super(EpisodeDeleteView, self).dispatch(*args, **kwargs)


class StreamSetupCreateView(CreateView):
    template_name = "radioportal/dashboard/streamsetup_edit.html"
    success_url = '/dashboard/streamsetup/%(id)s/'
    form_class = forms.StreamSetupPlainCompoundForm
    model = StreamSetup

    def get_form_class(self):
        form_class = super(StreamSetupCreateView, self).get_form_class()
        qs = get_objects_for_user(self.request.user, "change_show", Show)
        form_class.form_classes[0].base_fields['show'].queryset = qs
        return form_class

    @method_decorator(permission_required('create_streamsetup'))
    def dispatch(self, *args, **kwargs):
        return super(StreamSetupCreateView, self).dispatch(*args, **kwargs)


class StreamSetupEditView(UpdateView):
    template_name = "radioportal/dashboard/streamsetup_edit.html"
    success_url = '/dashboard/streamsetup/%(id)s/'
    form_class = forms.StreamSetupCompoundForm
    model = StreamSetup

    def get_form_class(self):
        form_class = super(StreamSetupEditView, self).get_form_class()
        qs = get_objects_for_user(self.request.user, "change_show", Show)
        form_class.form_classes[0].base_fields['show'].queryset = qs
        return form_class

    def get_context_data(self, **kwargs):
        ctx = super(StreamSetupEditView, self).get_context_data(**kwargs)
        ctx['show'] = self.object.show
        return ctx

    def get_form_kwargs(self):
        kwargs = super(StreamSetupEditView, self).get_form_kwargs()
        kwargs['extra'] = 1
        kwargs['can_delete'] = self.request.user.has_perm('change_stream', self.object)
        return kwargs

    #FIXME
    @method_decorator(permission_required('change_streamsetup', (StreamSetup, 'pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(StreamSetupEditView, self).dispatch(*args, **kwargs)

class StreamSetupDeleteView(DeleteView):
    template_name = "radioportal/dashboard/streamsetup_delete.html"
    success_url = "/dashboard/"
    model = StreamSetup

    @method_decorator(permission_required('delete_streamsetup', (StreamSetup, 'pk', 'pk')))
    def dispatch(self, *args, **kwargs):
        return super(StreamSetupDeleteView, self).dispatch(*args, **kwargs)
