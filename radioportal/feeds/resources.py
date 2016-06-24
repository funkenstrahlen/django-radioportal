from radioportal.models import Show, Episode, Stream

from django.conf import settings
from django.conf.urls import url
from django.db.models.aggregates import Min
from django.utils.timezone import is_naive

from easy_thumbnails.alias import aliases
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

import urlparse
import pytz

from tastypie.serializers import Serializer


class MyDateSerializer(Serializer):
    """
    Our own serializer to format datetimes in ISO 8601 but with timezone
    offset.
    """
    def format_datetime(self, data):
        # If naive or rfc-2822, default behavior...
        if is_naive(data) or self.datetime_formatting == 'rfc-2822':
            return super(MyDateSerializer, self).format_datetime(data)
        data = data.replace(microsecond=0)
        return data.isoformat()


class StreamResource(ModelResource):
    url = fields.CharField("get_absolute_url")

    class Meta:
        queryset = Stream.objects.filter(running=True)
        list_allowed_methods = ["get", ]
        include_resource_uri = False
        fields = ["codec", "bitrate", "container", "transport"]


class EpisodeResource(ModelResource):
    podcast = fields.ForeignKey('radioportal.feeds.resources.PodcastResource', 'show')

    begin = fields.DateTimeField('begin')

    def dehydrate_begin(self, bundle):
        tz = pytz.timezone(settings.TIME_ZONE)
        begin = bundle.obj.begin
        if begin:
            begin = tz.localize(begin)
        return begin

    end = fields.DateTimeField('end')

    def dehydrate_end(self, bundle):
        tz = pytz.timezone(settings.TIME_ZONE)
        end = bundle.obj.end()
        if end:
            end = tz.localize(end)
        return end

    id = fields.CharField("uuid")
    slug = fields.CharField('slug')
    title = fields.CharField('title')
    description = fields.CharField('description')

    status = fields.CharField('status')
    shownotes = fields.CharField('current_part__shownotes_id', default="")

    streams = fields.ToManyField(StreamResource,
                                 attribute=lambda bundle: Stream.objects.filter(
                                     channel__currentEpisode=bundle.obj, running=True),
                                 full_list=True, full=True, default=[], null=True, blank=True)

    listeners = fields.IntegerField('channel__listener', default=-1)

    class Meta:
        queryset = Episode.objects.all().annotate(begin=Min('parts__begin'))
        serializer = MyDateSerializer()
        resource_name = "episode"
        list_allowed_methods = ["get", ]
        detail_allowed_methods = ["get", ]
        detail_uri_name = "uuid"
        include_absolute_url = True
        excludes = ("uuid",)
        filtering = {
            "status": ('exact', 'in'),
            # "begin": ('lte', 'lt', 'gt', 'gte', 'exact'),
            # "end": ('lte', 'lt', 'gt', 'gte', 'exact'),
            "podcast": ALL_WITH_RELATIONS,
        }
        ordering = [ 'begin', ]


class PodcastResource(ModelResource):
    name = fields.CharField("name")
    subtitle = fields.CharField("description")
    description = fields.CharField("abstract")
    id = fields.CharField("uuid")
    slug = fields.CharField("slug")
    website_url = fields.CharField("url")
    feed_url = fields.CharField(attribute="podcastfeed__feed_url")
    email = fields.CharField("public_email")

    irc_url = fields.CharField("chat")
    webchat_url = fields.CharField("chat")
    twitter_handle = fields.CharField("twitter")
    donation_url = fields.CharField("donation_url")

    episodes = fields.ToManyField('radioportal.feeds.resources.EpisodeResource', 'episode_set', related_name='show')

    artwork = fields.DictField()

    def dehydrate_artwork(self, bundle):
        artworks = {}
        if not bundle.obj.icon:
            return artworks
        for name, settings in aliases.all(target='radioportal.Show.icon').iteritems():
            if not "v2" in name:
                continue
            thumb = bundle.obj.icon.get_existing_thumbnail(settings)
            if thumb:
                artworks[settings['size'][0]] = thumb.url
        return artworks

    def dehydrate_webchat_url(self, bundle):
        u = urlparse.urlparse(bundle.data["webchat_url"])
        channel = u.fragment
        if not channel:
            channel = u.path[1:]
        if "freenode" in u.netloc:
            return "https://webchat.freenode.net/?channels=%s" % channel
        elif "hackint" in u.netloc:
            return "https://webirc.hackint.org/?channel=#%s" % channel
        else:
            return bundle.data["webchat_url"]

    class Meta:
        queryset = Show.objects.all()
        resource_name = "podcast"
        list_allowed_methods = ["get", ]
        detail_allowed_methods = ["get", ]
        detail_uri_name = "uuid"
        include_absolute_url = True
        fields = ["name", "subtitle", "description", "slug", "artwork_thumb",
                  "website_url", "irc_url", "webchat_url", "twitter_handle",
                  "id"]
        filtering = {
            "id": ('exact',),
        }

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<uuid>\w[\w/-]*)/episodes%s$" %
                (self._meta.resource_name, trailing_slash()), self.wrap_view('get_episodes'), name="api_get_episodes"),
        ]

    def get_episodes(self, request, **kwargs):
        episode_resource = EpisodeResource()
        return episode_resource.get_list(request, podcast__id=kwargs["uuid"])

class PodcastResourceV1(PodcastResource):
    artwork = fields.DictField()

    def dehydrate_artwork(self, bundle):
        artworks = {}
        if not bundle.obj.icon:
            return artworks
        artworks["original"] = bundle.obj.icon.url
        for name, settings in aliases.all(target='radioportal.Show.icon').iteritems():
            if not "v1" in name:
                continue
            thumb = bundle.obj.icon.get_existing_thumbnail(settings)
            if thumb:
                artworks[settings['size'][0]] = thumb.url
        return artworks
