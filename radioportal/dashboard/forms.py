'''
Created on 14.09.2011

@author: robert
'''

from django import forms
from django.contrib.admin import widgets as adminwidgets
from django.forms import widgets

from datetime import timedelta
from django.forms.util import ErrorList

from radioportal import models
from django.utils.safestring import mark_safe
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.forms.widgets import Media, HiddenInput
from radioportal.models import StreamSetup, RecodedStream, SourcedStream, Stream

class EpisodeForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = models.Episode
        fields = ('slug', )

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
    duration = forms.TypedChoiceField(choices=DURATIONS, coerce=float, empty_value=0.0)
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



class StreamSetupForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = models.StreamSetup
        exclude = ('running', 'streamCurrentSong', 'streamGenre', 'streamShow',
                   'streamDescription', 'streamURL', 'currentEpisode', 'feed',
                   'graphic_differ_by', 'graphic_title')


class StreamForm(forms.ModelForm):
    required_css_class = "required"
    mount = forms.RegexField(regex='^[a-zA-Z0-9_-]+\.(mp3|ogg|ogm|oga|aac)$')


class SourcedStreamForm(StreamForm):
    required_css_class = "required"
    class Meta:
        model = models.SourcedStream
        fields = ('mount', 'user', 'password', 'encoding', 'fallback')
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

StreamFormSet = inlineformset_factory(StreamSetup, Stream, form=StreamForm)

SourcedStreamFormSet = inlineformset_factory(StreamSetup, SourcedStream, form=SourcedStreamForm)
RecodedStreamFormSet = inlineformset_factory(StreamSetup, RecodedStream, form=RecodedStreamForm)

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

class StreamSetupPlainCompoundForm(CompoundModelForm):
    required_css_class = "required"
    form_classes = [
        StreamSetupForm,
    ]
    
class StreamSetupCompoundForm(CompoundModelForm):
    required_css_class = "required"
    form_classes = [
        StreamSetupForm,
        SourcedStreamFormSet,
        RecodedStreamFormSet,
    ]
