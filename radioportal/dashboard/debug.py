from django.views.generic.edit import FormView
from radioportal.models import Stream
from radioportal.messages.receive import BackendInterpreter
from django import forms
from django_hosts.resolvers import reverse


class FakeStreamForm(forms.Form):
    def stream_choices():
        streams = Stream.objects.values('id', 'channel__cluster', 'mount')
        streams = map(lambda x: (x['id'], "%s: %s" % (x['channel__cluster'], x['mount'])), streams)
        return streams

    stream = forms.TypedChoiceField(choices=stream_choices, coerce=int)
    title = forms.CharField()
    url = forms.URLField()

class FakeStreamView(FormView):
    template_name = 'radioportal/dashboard/debug/fake_stream.html'
    form_class = FakeStreamForm
    
    def get_success_url(self):
        return reverse('debug-fake-stream', host='dashboard')

    def form_valid(self, form):
        stream = Stream.objects.get(id=form.cleaned_data['stream'])
        bi = BackendInterpreter()
        bi.channel_startmaster({'name': stream.channel.cluster, 'metadata': {'name': form.cleaned_data['title']}})
        if stream.mount.endswith("mp3"):
            bi.stream_start({'name': "/%s" % stream.mount, 'quality': '128k', 'format': 'mp3', 'type': 'http'})
        else:
            bi.stream_start({'name': "/%s" % stream.mount, 'quality': '128k', 'format': 'vorbis', 'type': 'http'})
        return super(FakeStreamView, self).form_valid(form)

