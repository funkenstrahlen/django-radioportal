from tastypie.api import Api

from .resources import PodcastResource, EpisodeResource

from .resources import PodcastResourceV1

v1_api = Api(api_name='v1')
v1_api.register(PodcastResourceV1())
v1_api.register(EpisodeResource())

v2_api = Api(api_name='v2')
v2_api.register(PodcastResource())
v2_api.register(EpisodeResource())

api_urls = v1_api.urls + v2_api.urls
