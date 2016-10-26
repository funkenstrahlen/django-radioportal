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

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from django_hosts.resolvers import reverse
from guardian.decorators import permission_required

from radioportal.dashboard.signup import forms
from radioportal.models import ShowRequest


class ShowRequestCreateView(CreateView):
    form_class = forms.ShowRequestCreateForm
    model = ShowRequest
    template_name = "radioportal/dashboard/showrequest_edit.html"

    def get_context_data(self, **kwargs):
        kwargs['action'] = _("Request a new Show")
        return super(ShowRequestCreateView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.create_time = datetime.now()
        return super(ShowRequestCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('dashboard', host='dashboard')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ShowRequestCreateView, self).dispatch(*args, **kwargs)


class ShowRequestAcceptView(UpdateView):
    form_class = forms.ShowRequestAcceptForm
    model = ShowRequest
    template_name = "radioportal/dashboard/showrequest_edit.html"
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        kwargs['action'] = _("Accept Request for Show")
        return super(ShowRequestAcceptView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.reviewer = self.request.user
        form.instance.review_time = datetime.now()
        form.instance.status = "ACCEPTED"
        return super(ShowRequestAcceptView, self).form_valid(form)

    def get_success_url(self):
        return reverse('dashboard', host='dashboard')

    @method_decorator(permission_required('radioportal.change_showrequest'))
    def dispatch(self, *args, **kwargs):
        return super(ShowRequestAcceptView, self).dispatch(*args, **kwargs)


class ShowRequestDenyView(UpdateView):
    form_class = forms.ShowRequestDenyForm
    model = ShowRequest
    template_name = "radioportal/dashboard/showrequest_edit.html"
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        kwargs['action'] = _("Deny Request for Show")
        return super(ShowRequestDenyView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.reviewer = self.request.user
        form.instance.review_time = datetime.now()
        form.instance.status = "DECLINED"
        return super(ShowRequestDenyView, self).form_valid(form)

    def get_success_url(self):
        return reverse('dashboard', host='dashboard')

    @method_decorator(permission_required('radioportal.change_showrequest'))
    def dispatch(self, *args, **kwargs):
        return super(ShowRequestDenyView, self).dispatch(*args, **kwargs)


class ShowRequestView(DetailView):
    model = ShowRequest
    template_name = "radioportal/dashboard/showrequest.html"
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        kwargs['deny'] = forms.ShowRequestDenyForm(self.request.POST, instance=self.object)
        kwargs['accept'] = forms.ShowRequestAcceptForm(self.request.POST, instance=self.object)
        return super(ShowRequestView, self).get_context_data(**kwargs)

    @method_decorator(permission_required('radioportal.change_showrequest'))
    def dispatch(self, *args, **kwargs):
        return super(ShowRequestView, self).dispatch(*args, **kwargs)
