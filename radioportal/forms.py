from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.contrib.admin import widgets
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import SiteProfileNotAvailable
from django.conf import settings

from radioportal import models


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        f = self.fields.get('permissions', None)
        if f is not None:
            perms = ['add_show', 'add_channel']
            f.queryset = Permission.objects.filter(codename__in=perms)
            f.queryset = f.queryset.select_related('content_type')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ('password', 'is_staff', 'is_superuser',
                   'last_login', 'date_joined', 'user_permissions', 'groups')

from django.contrib.auth import forms as authforms


def save(self, commit=True):
    if hasattr(settings, "REALM"):
        realm = settings.REALM
    else:
        realm = "Default Realm"
    try:
        profile = self.user.get_profile()
        profile.set_htdigest(self.cleaned_data['new_password1'], realm)
    except models.UserProfile.DoesNotExist:
        profile = models.UserProfile(user=self.user)
        profile.save()
        profile.set_htdigest(self.cleaned_data['new_password1'], realm)
    except SiteProfileNotAvailable:
        pass
    self.user.set_password(self.cleaned_data['new_password1'])
    if commit:
        self.user.save()
    return self.user

authforms.SetPasswordForm.save = save

