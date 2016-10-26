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

from django import forms
from django.utils.translation import ugettext_lazy as _

from radioportal.models import ShowRequest, Show

class ShowRequestAcceptForm(forms.ModelForm):
    required_css_class = "required"

    class Meta:
        model = ShowRequest
        fields = ()


class ShowRequestDenyForm(forms.ModelForm):
    required_css_class = "required"

    class Meta:
        model = ShowRequest
        fields = ('review_note',)


class ShowRequestCreateForm(forms.ModelForm):
    required_css_class = "required"

    def clean_name(self):
        data = self.cleaned_data['name']
        if Show.objects.filter(name__iexact=data).count() > 0 or ShowRequest.objects.filter(name__iexact=data).count() > 0:
            raise forms.ValidationError(_("This name is already used for a show"))
        return data

    class Meta:
        model = ShowRequest
        fields = ('name', 'feed', 'ical')


class Signup(ShowRequestCreateForm):
    agb = forms.BooleanField(required=True, 
                             help_text=_("I read and understood the conditions"), 
                             label=_("""
Hiermit versichere ich, dass der von mir ueber den Service von xenim streaming veroeffentlichte Podcast
den gesetzlichen Vorgaben entspricht. Insbesondere versichere ich, dass die von mir uebermittelten Inhalte
frei von Rechten Dritter (Urheberrecht, Markenrechte, Persoenlichkeitsrechte, etc.) sind oder mir die 
Erlaubnis des/der Rechteinhaber zur Veroeffentlichung erteilt wurde. Der von mir veroeffentlichte Stream
beinhaltet keine rechtswidrigen, strafbaren, pornografische, verunglimpfende oder persoenlichkeitsrechtsverletzende
Inhalte. Ich stelle die Betreiber von xenim streaming insoweit von jeglicher Haftung fuer die bereitgestellten Inhalte frei.
    """))

    def signup(self, request, user):
        show_request = super(ShowRequestCreateForm, self).save(commit=False)
        show_request.user = user
        show_request.status = "UNCONFIR"
        show_request.save()

