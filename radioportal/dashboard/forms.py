'''
Created on 14.09.2011

@author: robert
'''

from django import forms
from django.contrib.admin import widgets as adminwidgets
from django.forms import widgets
from django.utils.translation import ugettext as _

from datetime import timedelta
from django.forms.util import ErrorList

from radioportal import models
from django.utils.safestring import mark_safe
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.forms.widgets import Media, HiddenInput, SelectMultiple
from radioportal.models import Channel, RecodedStream, SourcedStream, Stream

import jsonfield.forms

from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from itertools import chain

from radioportal import messages

class CheckboxSelectMultipleTable(forms.SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [] #[u'</td>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.widgets.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<label%s>%s %s</label></td><td>' % (label_for, rendered_cb, option_label))
        #output.append(u'<td>')
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
    id_for_label = classmethod(id_for_label)


from guardian import shortcuts

class PermissionForm(forms.Form):
    def __init__(self, user, model, *args, **kwargs):
        self.user = user
        self.model = model
        super(PermissionForm, self).__init__(*args, **kwargs)
        qs = self.model.objects.all()
        #qs = qs.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        for instance in qs:
            self.fields[unicode(instance.pk)] = forms.MultipleChoiceField(
                        label=self.get_obj_perms_field_label(instance),
                        choices=self.get_obj_perms_field_choices(),
                        initial=self.get_obj_perms_field_initial(instance),
                        widget=CheckboxSelectMultipleTable,
                        required=False)

    def get_obj_perms_field_label(self, instance):
        return unicode(instance)

    def get_obj_perms_field_choices(self):
        """
        Returns choices for object permissions management field. Default:
        list of tuples ``(codename, name)`` for each ``Permission`` instance
        for the managed object.
        """
        choices = []
        for p in shortcuts.get_perms_for_model(self.model):
            if not p.codename.startswith("add_") and not p.codename.startswith("delete_"):
                choices.append((p.codename, p.codename))
        return choices

    def get_obj_perms_field_initial(self, obj):
        perms = shortcuts.get_perms(self.user, obj)
        return perms
    
    def save_obj_perms(self):
        """
        Saves selected object permissions by creating new ones and removing
        those which were not selected but already exists.

        Should be called *after* form is validated.
        """
        for item in self.cleaned_data:
            instance = self.model.objects.get(pk=item)
            perms = self.cleaned_data[item]
            model_perms = [c[0] for c in self.get_obj_perms_field_choices()]

            to_remove = set(model_perms) - set(perms)
            for perm in to_remove:
                shortcuts.remove_perm(perm, self.user, instance)

            for perm in perms:
                shortcuts.assign(perm, self.user, instance)


class EpisodeForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = models.Episode
        fields = ('slug', 'status')

class EpisodePartForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = models.EpisodePart
        widgets = {
            'begin': adminwidgets.AdminSplitDateTime(),
            'end': adminwidgets.AdminSplitDateTime(),
            'episode': widgets.HiddenInput(),
        }

class CreateEpisodeForm(EpisodeForm):
    required_css_class = "required"
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        #self.base_fields['show'].widget.is_hidden = True
        super(CreateEpisodeForm, self).__init__(data, files, auto_id, prefix,
                initial, error_class, label_suffix, empty_permitted, instance)

    
    DURATIONS=(
        (0.0, '--'),
        (0.5, '0.5h'),
        (1.0, '1.0h'),
        (1.5, '1.5h'),
        (2.0, '2.0h'),
        (2.5, '2.5h'),
        (3.0, '3.0h'),
        (3.5, '3.5h'),
        (4.0, '4.0h'),
        (4.5, '4.5h'),
        (5.0, '5.0h'),
        (5.5, '5.5h'),
   )
    duration = forms.TypedChoiceField(choices=DURATIONS, coerce=float, empty_value=0.0, label=_("Duration"))
    slug = forms.SlugField()
    
    def save(self, commit=True):
        if self.instance.begin and not self.cleaned_data['duration'] == 0.0:
            td = timedelta(hours=self.cleaned_data['duration'])
            self.instance.end = self.instance.begin + td 
        return EpisodeForm.save(self, commit)
    
    class Meta:
        model = models.EpisodePart
        exclude = ('status','end', 'episode')
        fields = ('slug', 'title', 'description', 'begin', 'duration', 'url')
        widgets = {
            'begin': adminwidgets.AdminSplitDateTime(),
            #'episode': HiddenInput(),
        }


class OrderedSelectMultiple(SelectMultiple):

    def render_options(self, choices, selected_choices):
        selected_choices = list(force_unicode(v) for v in selected_choices)
        choices = list(chain(self.choices, choices))
        iterchoices = []
        for c in selected_choices:
            for t in choices:
                if t[0] == c:
                    iterchoices.append(t)
        for t in (set(choices) - set(iterchoices)):
            iterchoices.append(t)
        output = []
        for option_value, option_label in iterchoices: #chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                output.append(u'</optgroup>')
            else:
                output.append(self.render_option(selected_choices, option_value, option_label))
        return u'\n'.join(output)
     	
    class Media:
        js = (
           'jquery-ui/js/jquery-1.6.2.min.js',
           'jquery-ui/js/jquery-ui-1.8.17.custom.min.js',
           'asmselect/jquery.asmselect.js',
        )
        css = {
           'all': ('asmselect/jquery.asmselect.css',),
        }


class ChannelForm(forms.ModelForm):
    required_css_class = "required"
    mapping_method = jsonfield.forms.JSONFormField #widget=OrderedSelectMultiple(choices=MAPPINGS))
    class Meta:
        MAPPINGS=(
          ('guess-from-last', _("Create new episode, get episode number by adding one to last episode number")),
          ('append-to-live', _("Append new episode part to generic episode \"live\"")),
          ('nothing','nothing'),
          ('default', _("Default")),)
    
        model = models.Channel
        exclude = ('running', 'streamCurrentSong', 'streamGenre', 'streamShow',
                   'streamDescription', 'streamURL', 'currentEpisode', 'feed',
                   'graphic_differ_by', 'graphic_title')
        widgets = {
            'mapping_method': OrderedSelectMultiple(choices=messages.episode_finder_list()),
        }


class StreamForm(forms.ModelForm):
    required_css_class = "required"
    mount = forms.RegexField(regex='^[a-zA-Z0-9_-]+\.(mp3|ogg|ogm|oga|aac)$')


class SourcedStreamForm(StreamForm):
    required_css_class = "required"
    class Meta:
        model = models.SourcedStream
        fields = ('mount', 'user', 'password', 'encoding')
#    class Media:
#        js = ('http://code.jquery.com/jquery-1.6.1.min.js', 'dashboard/stream.js',)


class RecodedStreamForm(StreamForm):
    required_css_class = "required"
    class Meta:
        model = models.RecodedStream
        fields = ('mount', 'bitrate', 'format', 'source')


class ShowForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = models.Show

class ShowFeedForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = models.ShowFeed
        widgets = {
            'show': HiddenInput(),
        }
     

FeedFormSet = inlineformset_factory(models.Show, models.ShowFeed)

StreamFormSet = inlineformset_factory(Channel, Stream, form=StreamForm)

SourcedStreamFormSet = inlineformset_factory(Channel, SourcedStream, form=SourcedStreamForm)
RecodedStreamFormSet = inlineformset_factory(Channel, RecodedStream, form=RecodedStreamForm)

class GraphicForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = models.Graphic
        exclude = ('file',)


#GraphicFormSet = inlineformset_factory(models.Episode, models.Graphic,
#                                    extra=0, can_delete=True, form=GraphicForm)

class RecordingForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = models.Recording
        exclude = ('publicURL', 'path', 'format', 'bitrate', 'size')

#RecordingFormSet = inlineformset_factory(models.Episode,
#                                    models.Recording, extra=0, form=RecordingForm)

class CompoundModelForm:
    required_css_class = "required"
    form_classes = []
    
    def __init__(self, *args, **kwargs):
        if "initial" in kwargs:
            del kwargs["initial"]
        self.forms = []
        for form in self.form_classes:
            kw = {}
            kw.update(kwargs)
            if issubclass(form, BaseInlineFormSet):
                if "initial" in kw:
                    del kw["initial"]
                if 'can_delete' in kw:
                    form.can_delete = kw["can_delete"]
                if 'extra' in kw:
                    form.extra = kw["extra"]
            if "can_delete" in kw:
                del kw["can_delete"]
            if "extra" in kw:
                del kw["extra"]     
            self.forms.append(form(*args, **kw))

    def _get_media(self):
        """
        Provide a description of all media required to render the widgets on this form
        """
        media = Media()
        for form in self.forms:
            media = media + form.media
        return media

    media = property(_get_media)

    def is_valid(self):
        """
        Returns True if all subforms are either valid or
        empty and not required. False otherwise.
        """
        # first check if we're bound ...
        if self.is_bound:
            # then check every subform ...
            for form in self.forms:
                if not form.is_valid():
                    return False
        else:
            return False
        return True

    def save(self):
        objects = []
        for form in self.forms:
            objects.append(form.save())
        self.__dict__ = objects[0].__dict__
        return objects[0]

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        subs = []
        for f in self.forms:
            if issubclass(type(f), BaseInlineFormSet):
                subs.append('<tr><td colspan="2"><h3>%s %s</h3></td></tr>' % (_('Associated'), f.model.__name__))
            subs.append(f.as_table())
        return mark_safe("\n".join(subs))

    def as_ul(self):
        "Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."
        subs = []
        for f in self.forms:
            subs.append(f.as_ul())
        return mark_safe("\n".join(subs))

    def as_p(self):
        "Returns this form rendered as HTML <p>s."
        subs = []
        for f in self.forms:
            subs.append(f.as_p())
        return mark_safe("\n".join(subs))
    
    def is_bound(self):
        return True

class ChannelPlainCompoundForm(CompoundModelForm):
    required_css_class = "required"
    form_classes = [
        ChannelForm,
    ]
    
class ChannelCompoundForm(CompoundModelForm):
    required_css_class = "required"
    form_classes = [
        ChannelForm,
        SourcedStreamFormSet,
        RecodedStreamFormSet,
    ]
