from tastypie.api import Api

from .resources import PodcastResource, EpisodeResource

v1_api = Api(api_name='v1')
v1_api.register(PodcastResource())
v1_api.register(EpisodeResource())
