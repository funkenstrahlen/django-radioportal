

from django import forms
from django.views.generic.edit import UpdateView
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext_lazy as _

from guardian.mixins import PermissionRequiredMixin
from django_hosts.resolvers import reverse

from radioportal.models import ICalFeed, Show


class ICalForm(forms.ModelForm):
    class Meta:
        model = ICalFeed
        exclude = ('show',)
#        widgets = {
#            'show': HiddenInput(),
#        }
        labels = {
            'url': _("ICal Feed URL"),
            'slug_regex': _("Episode Slug"),
            'title_regex': _("Episode Title"),
            'description_regex': _("Episode Description"),
            'url_regex': _("Episode URL"),
            'filter_regex': _("Ignore Episode Filter"),
            'delete_missing': _("Delete upcoming Episodes not in iCal anymore")
        }



class ICalEditView(PermissionRequiredMixin, UpdateView):
    form_class = ICalForm
    model = ICalFeed
    slug_field = 'show__slug'
    template_name = "radioportal/dashboard/importer_ical.html"
    
    permission_required = 'change_show'
    
    def get_permission_object(self):
        return Show.objects.get(slug=self.kwargs["slug"])

    def get_success_url(self):
        return reverse( 'admin-show-ical', kwargs={'slug': self.object.show.slug}, host="dashboard")
