# -*- coding: utf-8 -*-

from django.conf import settings

from django import template
register = template.Library()


@register.filter
def startswith(value, arg):
    """Usage, {% if value|starts_with:"arg" %}"""
    if not value:
        return False
    return value.startswith(arg)


@register.filter
def contains(value, arg):
    """Usage, {% if value|contains:"arg" %}"""
    return arg in value


@register.filter
def hashEpisode(episode, what):
    if what == "content":
        val = episode.description
        val += episode.title
        val += episode.currentSong
        val += episode.genre
        return hash()
    if what == "streams":
        if episode.streamsetup:
            val = episode.streamsetup.stream_set.values_list('id', 'running')
            return hash(val)
        else:
            return 0


@register.filter
def object_name(value):
    return value._meta.object_name


@register.filter
def formataudio(number, format):
    """Usage: {{ stream.bitrate|formataudio:stream.format }}"""
    if format == "mp3":
        if number[-1] == 'k':
            number = number[:-1]
        return "%sKBit/s" % (number,)
    elif format == "ogg":
        if "q" in number:
            return "Quality %s" % (number[1:],)
        else:
            if number[-1] == 'k':
                number = number[:-1]
            return "%sKBit/s" % (number,)
    else:
        return number

from django.template import Node
from django.utils.encoding import smart_str


# copied from django.template.defaulttags to support custom urlconf
class URLNode(Node):
    def __init__(self, view_name, args, kwargs, asvar, legacy_view_name=True):
        self.view_name = view_name
        self.legacy_view_name = legacy_view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        from django.core.urlresolvers import reverse, NoReverseMatch
        args = [arg.resolve(context) for arg in self.args]
        urlconf = None
        if "urlconf" in self.kwargs:
            urlconf = str(self.kwargs["urlconf"])
            del self.kwargs["urlconf"]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        view_name = self.view_name
        if not self.legacy_view_name:
            view_name = view_name.resolve(context)

        # Try to look up the URL twice: once given the view name, and again
        # relative to what we guess is the "main" app. If they both fail,
        # re-raise the NoReverseMatch unless we're using the
        # {% url ... as var %} construct in which cause return nothing.
        url = ''
        try:
            url = reverse(view_name, urlconf=urlconf, args=args,
                          kwargs=kwargs, current_app=context.current_app)
        except NoReverseMatch, e:
            if settings.SETTINGS_MODULE:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                try:
                    url = reverse(project_name + '.' + view_name,
                              args=args, kwargs=kwargs,
                              current_app=context.current_app)
                except NoReverseMatch:
                    if self.asvar is None:
                        # Re-raise the original exception, not the one with
                        # the path relative to the project. This makes a
                        # better error message.
                        raise e
            else:
                if self.asvar is None:
                    raise e

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url

from django.template import defaulttags
defaulttags.URLNode = URLNode
