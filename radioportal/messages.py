'''
Created on 09.08.2011

@author: robert
'''

from carrot.connection import DjangoBrokerConnection
from carrot.messaging import Publisher, Consumer
from django.core.serializers import json
from pkg_resources import StringIO
from django.utils import simplejson
from django.core.serializers.python import Deserializer as PythonDeserializer
from django.utils.datetime_safe import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from django.db.models import Min
from django.conf import settings

import radioportal

import logging

logger = logging.getLogger(__name__)

import re, urlparse, urllib, os.path, urllib2
import easy_thumbnails.files

from radioportal.models import RecodedStream, SourcedStream, Channel, ShowFeed, UserProfile,\
        Episode, EpisodePart, Stream, Graphic, Recording, Show

from radioportal_auphonic.models import AuphonicSettings

from url_normalize import url_normalize

import dateutil.parser

#### Part one: sending notifications for changed objects ####

class DTO(object):
    def serialize(self):
        return simplejson.dumps((self.__dict__,))

class DTOSourcedStream(DTO):
    def __init__(self, instance):
        self.mount = instance.mount
        self.user = instance.user
        self.password = instance.password
        self.encoding = instance.encoding
        self.cluster = instance.channel.cluster
        self.fallback = instance.fallback
        self.id = instance.pk

class DTOShowFeed(DTO):
    def __init__(self, instance):
        self.enabled = instance.enabled
        self.feed = instance.feed
        self.ical = instance.icalfeed
        self.title_regex = instance.titlePattern
        self.show = instance.show.slug
        self.id = instance.pk

class DTOUserProfile(DTO):
    def __init__(self, instance):
        self.id = instance.pk
        self.htdigest = instance.htdigest

class DTOShow(DTO):
    def __init__(self, instance):
        self.slug = instance.slug
        self.cluster = instance.channel.cluster
        self.twitter = instance.twitter
        self.chat = instance.chat

class DTOAuphonic(DTO):
    def __init__(self, instance):
        self.channel = instance.channel.cluster
        if instance.preset:
            self.preset = instance.preset.uuid
        else:
            self.preset = ""
        self.update_md = instance.update_metadata
        self.enabled = instance.enabled
        self.oauth_token = instance.oauth_token
        self.id = self.channel

dto_map = {
    "sourcedstream": DTOSourcedStream,
    "showfeed": DTOShowFeed,
    "userprofile": DTOUserProfile,
    "auphonicsettings": DTOAuphonic,
}

class DTOSerializer(object):
    def serialize(self, instance):
        name = instance._meta.object_name.lower()
        if name in dto_map:
            return dto_map[name](instance).serialize()
        else:
            return json.Serializer().serialize((instance,))

#dto_serializer = DTOSerializer()
dto_serializer = json.Serializer()

def object_changed(sender, instance, created, **kwargs):
    conn = DjangoBrokerConnection()
    action = "created" if created else "changed"
    publisher = Publisher(connection=conn,
        exchange="django", 
        routing_key="%s.%s.%s" % (sender._meta.app_label, sender._meta.module_name, action),
        exchange_type="topic",
    )
    data = DTOSerializer().serialize(instance)
    publisher.send(data) 
    publisher.close()
    conn.close()
    logger.debug("Object change message for %s sent" % unicode(instance))

def object_deleted(sender, instance, **kwargs):
    conn = DjangoBrokerConnection()
    publisher = Publisher(connection=conn,
        exchange="django", 
        routing_key="%s.%s.deleted" % (sender._meta.app_label, sender._meta.module_name),
        exchange_type="topic",
    )
    data = DTOSerializer().serialize(instance)
    publisher.send(data)
    publisher.close()                  
    conn.close()
    logger.debug("Object delete message for %s sent" % unicode(instance))

#### Part two: receiving updates ####

def DTODeserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
#    if isinstance(stream_or_string, basestring):
#        stream = StringIO(stream_or_string)
#    else:
#        stream = stream_or_string
#    print stream
    objs = simplejson.loads(stream_or_string)
    newob = {}
    newob['fields'] = objs
    newob['pk'] = objs['pk']
    newob['model'] = objs['model']
    del newob['fields']['pk']
    del newob['fields']['model']
    newob = [newob,]
    py_obs = PythonDeserializer(newob, **options)
    return py_obs.next()

class EpisodeFinder(object):
    def get_name(self):
        return "nothing"

    def get_description(self):
        return _("Does nothing.")

    def get_episode(self, channel, metadata):
        return None


class EpisodeSlugFromTitle(EpisodeFinder):
    def get_name(self):
        return "find-from-title"

    def get_description(self):
        return _("Try to find an existing episode with a slug,"+
           " which is the same as the first word of the stream name")

    def get_episode(self, channel, metadata):
        episode_slug = metadata['name'].split(" ")[0]
        episode_slug = re.sub(r'[^a-zA-Z0-9]+', '', episode_slug)
        print "episode_slug: ", episode_slug
        try:
            episode = Episode.objects.get(
                         show__in=channel.show.all(),
                         slug__iexact=episode_slug)
            return episode
        except Episode.MultipleObjectsReturned:
            logger.error("more than one episode found")
        except Episode.DoesNotExist:
            pass


class LatestPlannedEpisode(EpisodeFinder):
    def get_name(self):
        return "find-latest-planned"

    def get_description(self):
        return _("Try to find the earliest possible, existing, upcoming episode")

    def get_episode(self, channel, metadata):
        try:
            episode = Episode.objects.filter(
                        show__in=channel.show.all(), 
                        status='UPCOMING').annotate(
                           begin=Min('parts__begin')).order_by('begin')[0]
            return episode
        except:
            pass


class MakeEpisodeMixin(object):
    def _make_episode(self, show, number):
        episode_slug = "%s%03i" % (show.defaultShortName, 
                    number)
        return self._make_episode_slug(show, episode_slug)

    def _make_episode_slug(self, show, slug):
        episode = Episode(show=show, slug=slug, status=Episode.STATUS[1][0])
        episode.save()
        return episode


class MakeEpisodeFromNumberInShow(EpisodeFinder, MakeEpisodeMixin):
    def get_name(self):
        return "make-from-number-in-show"

    def get_description(self):
        return _("Create a new episode using the episodeNumber stored in the show")

    def get_episode(self, channel, metadata):
        for show in channel.show.all():
            show.nextEpisodeNumber += 1
            show.save()
            return self._make_episode(show, show.nextEpisodeNumber)

class MakeEpisodeFromLastEpisode(EpisodeFinder, MakeEpisodeMixin):
    def get_name(self):
        return "make-from-number-of-last-episode"

    def get_description(self):
        return _("Create a new episode by incrementing the number of" +
                 " the last episode by one")

    def get_episode(self, channel, metadata):
        last_episode = Episode.objects.filter(
                        show__in=channel.show.all(), 
                        status='ARCHIVED').annotate(
                         begin=Min('parts__begin')).order_by('-begin')[0]
        id_str = re.sub(r'[^0-9]+', '', last_episode.slug)
        if id_str == '':
            id_str = '0'
        id = int(id_str) + 1
        return self._make_episode(last_episode.show, id)

class FindLiveEpisode(EpisodeFinder, MakeEpisodeMixin):
    name = "live"
    def get_name(self):
        return "find-or-make-live"

    def get_description(self):
        return _("Find or create an episode named \"%s\"" % self.name)

    def get_episode(self, channel, metadata):
        for show in channel.show.all():
            try:
                live = Episode.objects.get(show=show, slug=self.name)
            except Episode.DoesNotExist:
                live = self._make_episode_slug(show, self.name)
            return live

import inspect, sys

def get_episode_finder():
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    finders = {}
    for name, cls in clsmembers:
        if issubclass(cls, EpisodeFinder):
            finders[cls().get_name()] = cls
    return finders

class episode_finder_list:
    def __iter__(self):    
        finders = get_episode_finder()
        doc_finders = {}
        for name, cls in finders.iteritems():
            doc_finders[name] = cls().get_description()
        return doc_finders.iteritems()
    def next(self):
        raise StopIteration

class BackendInterpreter(object):
    def show_startmaster(self, data):
        """
            value={'name': cpwd, 'time': int, 'show' : {'name': 'CR001 Titel der Sendung'}}
            FIXME: need show
        """
        data = simplejson.loads(data)
        channel = Channel.objects.get(cluster=data['name'])

        available_methods = get_episode_finder()
        episode = None

        for method in channel.mapping_method:
            #print "trying method", method
            if method not in available_methods:
                logger.warning("Mapping method %s not found" % method)
                continue
            finder = available_methods[method]()
            try:
                episode = finder.get_episode(channel, data['show'])
            except Exception, e:
                print "method", method, "failed"
                print traceback.format_exc()
                logger.warning("Mapping method %s failed: %s" % (method, e))
            if episode:
                break
                
        if not episode:
            logger.error("No episode found for cluster %s" % data['name'])
            return
        
        part = None
        if episode.status == Episode.STATUS[2][0]:
            parts = episode.parts.all().reverse()
            if len(parts) > 0:
                part = parts[0]
        if not part:
            part = EpisodePart(episode=episode)

        part.begin = datetime.now()
        part.save()                

        episode.status = "RUNNING"
        episode.current_part = part
        episode.save()

        channel.currentEpisode = episode
        channel.save()

    def show_stop(self, data):
        """
            value={'name': cpwd}
        """
        data = simplejson.loads(data)
        channel = Channel.objects.get(cluster=data['name'])
        if channel.currentEpisode:
            episode = channel.currentEpisode 
            part = episode.current_part
            part.end = datetime.now()
            part.save()
            episode.current_part = None
            episode.status = Episode.STATUS[0][0]
            episode.save()
            channel.currentEpisode = None
            channel.save()
        else:
            logger.error("show_stop: no current episode found for cluster %s" % data['name'])
            # FIXME
            

    def stream_start(self, data):
        """
            value={'name': mount, 'id': id, 'stream': {'mountpoint': 'mount.mp4', 'bitrate': 128, 'type': 'mp3'}}
            FIXME: Stream object
        """
        data = simplejson.loads(data)
        
        mp = data['stream']['mountpoint']
        
        stream = Stream.objects.filter(mount=mp)
        if len(stream) == 1:
            stream = stream[0]
        else:
            channel = Channel.objects.get(cluster=data['name'].split("-")[0])
            stream = Stream(mount=mp, channel=channel)
        stream.running = True
        stream.bitrate = data['stream']['bitrate']
        stream.format = data['stream']['type'].lower()
        stream.save()
        #stream.channel.updateRunning()
        
    def stream_stop(self, data):
        """
            value={'name': mount}
        """
        data = simplejson.loads(data)
        mount = data['name'].split("-")
        
        stream = Stream.objects.filter(channel__cluster=mount[0], format=mount[2].lower(), bitrate=int(mount[1]))
        if len(stream) == 1:
            stream = stream[0]
            stream.running = False
            stream.save()

    def show_metadata(self, data):
        """
            value={'name': mount, 'key': key, 'val': val}
        """
        data = simplejson.loads(data)
        
        channel = Channel.objects.get(cluster=data['name'].split("-")[0])
        
        # mapping internal keys to attributes of stream channel
        map2channel={'name': 'streamShow','genre':'streamGenre',
             'current_song': 'streamCurrentSong',
             'description':'streamDescription', 'url': 'streamURL'}
        if data['key'] in map2channel:
            setattr(channel, map2channel[data['key']], data['val'])
            channel.save()
        else:
            logger.debug("show_metadata: key %s not in channel map" % data['key'])
         
        # mapping between internal keys and episode fields
        map2eps={'name': 'title', 'description': 'description', 'url': 'url'}
        
        if channel.currentEpisode:
            episode = channel.currentEpisode
            part = episode.current_part
            if data['key'] == 'name' and data['val'].lower().startswith(episode.slug):
                data['val'] = data['val'][len(episode.slug):].strip()
            if data['key'] == 'url' and data['val'] != '':
                data['val'] = url_normalize(data['val'])
            if data['key'] in map2eps:
                setattr(part, map2eps[data['key']], data['val'])
                part.save()
        else:
            logger.error("show_metadata: no current episode for %s" % channel.cluster)
        
    def graphic_created(self, data):
        """
            value={'show': show, 'file': name})
        """
        data = simplejson.loads(data)
        
        cpwd = data['show'].split("-")[0]
        channel = Channel.objects.get(cluster=cpwd)
        
        g = Graphic(file='graphics/%s' % data['file'])
        
        if channel.currentEpisode:
            g.episode = channel.currentEpisode.current_part
        else:
            logger.error("graphic_create: no current episode for %s" % channel.cluster)
        
        g.save()
        
    def recording_start(self, data):
        data = simplejson.loads(data)
        
        cpwd = data["cluster"]
        
        channel = Channel.objects.get(cluster=cpwd)
        if channel.currentEpisode:
            part = channel.currentEpisode.current_part
        else:
            logger.error("recording_start: no current episode for %s" % channel.cluster)
            return
       
        r = Recording(episode=part)
        r.path = data['file']
        r.format = data['format']
        r.bitrate = data['bitrate']
        r.size = 0
        r.running = True
        r.save()
    
    def recording_stop(self, data):
        data = simplejson.loads(data)
        rec = Recording.objects.get(path=data['file'])
        rec.running = False
        rec.size = data['size']
        rec.save()

    def objects_get(self, data):
        data = simplejson.loads(data)
        type = ContentType.objects.get(app_label="radioportal", model=data['model'])
        model = type.model_class()
        name = model._meta.object_name.lower()
        if name not in dto_map:
            return
        objects = model.objects.all()
        Serializer = dto_map[name]
        plain_dict = []
        for o in objects:
            so = Serializer(o)
            plain_dict.append(so.__dict__)
        result = simplejson.dumps(plain_dict)
        
        conn = DjangoBrokerConnection()
        #print "key", "%s.%s.%s" % (model._meta.app_label, model._meta.module_name, "changed")
        publisher = Publisher(connection=conn,
            exchange="django", 
            routing_key="%s.%s.%s" % (model._meta.app_label, model._meta.module_name, "changed"),
            exchange_type="topic",
        )
        publisher.send(result) 
        publisher.close()
        conn.close()
        logger.debug("Object list to %s sent" % unicode(data['answer']))

    def feed_updated(self, data):
        data = simplejson.loads(data)
        if data['global']['type'] == 'calendar':
            try:
                show = Show.objects.get(slug=data['showid'])
            except Show.DoesNotExist:
                return
            for id, e in data['entries'].iteritems():
                slug = e['title'].split()[0] # get first word from title
                slug = re.sub("\W", "", slug) # remove non alpha numeric chars
                try:
                    ep = Episode.objects.get(show=show, slug=slug, status=Episode.STATUS[2][0])
                except Episode.DoesNotExist:
                    ep = Episode(show=show, slug=slug, status=Episode.STATUS[2][0])
                    ep.save()
                    epp = EpisodePart(episode=ep)
                    epp.begin = dateutil.parser.parse(e['begin'], ignoretz=True)
                    epp.save()
                    ep.current_part = epp
                    ep.save()
                epp = ep.current_part
                epp.begin = dateutil.parser.parse(e['begin'], ignoretz=True)
                if 'end' in e:
                    epp.end = dateutil.parser.parse(e['end'], ignoretz=True)
                if 'url' in e:
                    epp.url = e['url']
                if 'description' in e:
                    epp.description = e['description']
                title = e['title'].split(None, 1)
                if len(title) == 2:
                    epp.title = title[1]
                else:
                    epp.title = ""
                epp.save()
        elif data['global']['type'] == 'podcast':
            try:
                show = Show.objects.get(slug=data['showid'])
            except Show.DoesNotExist:
                return
            for item in ('url', 'description', 'abstract'):
                if item in data['global']:
                    setattr(show, item, data['global'][item])
            show.save()
            if 'icon' in data['global']:
                # print "got icon url: ", data['global']['icon']
                fetch_icon = True
                if show.icon:
                    # print "existing icon"
                    local_modtime = show.icon.get_source_modtime()
                    request = urllib2.Request(data['global']['icon'])
                    request.get_method = lambda : 'HEAD'
                    response = urllib2.urlopen(request)
                    time_s = response.headers['last-modified']
                    time_d = dateutil.parser.parse(time_s)
                    remote_modtime = time_d.strftime("%s")
                    # print "local time", local_modtime
                    # print "remote time", remote_modtime
                    # print "comparison: ", (int(remote_modtime) <= int(local_modtime))
                    if int(remote_modtime) <= int(local_modtime):
                        # print "don't fetch"
                        fetch_icon = False
                # print "fetch icon: ", fetch_icon
                if fetch_icon:
                    fname = urlparse.urlsplit(data['global']['icon']).path.split("/")[-1]
                    path = show._meta.get_field_by_name("icon")[0].upload_to
                    fname = os.path.join(settings.MEDIA_ROOT, path, "%s-%s" % (show.slug, fname))
                    # print "name to save to:", fname
                    file, info = urllib.urlretrieve (data['global']['icon'], fname)
                    # print "retrieve result: ", file, info
                    options = show._meta.get_field_by_name("icon")[0].resize_source
                    thumbnailer = easy_thumbnails.files.get_thumbnailer(file)
                    content = thumbnailer.generate_thumbnail(options)
                    # print content
                    show.icon = content
                    show.save()

import traceback

def process_message(message_data, message):
    try: 
        routing_key = message.delivery_info['routing_key']
        keys = routing_key.split(".", 1)
        if len(keys) != 2:
            logger.warning("routing_key %s to short" % routing_key)
            message.ack()
            return
        logger.debug("calling bi.%s_%s(data)" % (keys[0], keys[1]))
        
        bi = BackendInterpreter()
        if not hasattr(bi, '%s_%s' % (keys[0], keys[1])):
            logger.debug("no method for routing_key %s" % routing_key)
            message.ack()
            return
        message_data = message_data.decode("utf-8", 'replace')
        #print message_data
        getattr(bi, '%s_%s' % (keys[0], keys[1]))(message_data)
    except Exception as inst:
        print traceback.format_exc()
        logger.exception(inst)
    message.ack()

class AMQPInitMiddleware(object):
    def __init__(self):
        logger.info("Loading AMQP Middleware")
        self.send_messages()
        #self.receive_messages()
        from django.core.exceptions import MiddlewareNotUsed
        raise MiddlewareNotUsed()

    def send_messages(self):
        logger.info("Connecting model change signals to amqp")
        
        from django.db.models.signals import post_save, post_delete
        
        post_save.connect(object_changed, RecodedStream, dispatch_uid="my_dispatch_uid")
        post_save.connect(object_changed, SourcedStream, dispatch_uid="my_dispatch_uid")
        #post_save.connect(object_changed, Channel, dispatch_uid="my_dispatch_uid")
        post_save.connect(object_changed, ShowFeed, dispatch_uid="my_dispatch_uid")
        post_save.connect(object_changed, UserProfile, dispatch_uid="my_dispatch_uid")
        post_save.connect(object_changed, AuphonicSettings, dispatch_uid="my_dispatch_uid")

        
        post_delete.connect(object_deleted, RecodedStream, dispatch_uid="my_dispatch_uid")
        post_delete.connect(object_deleted, SourcedStream, dispatch_uid="my_dispatch_uid")
        #post_delete.connect(object_deleted, Channel, dispatch_uid="my_dispatch_uid")
        post_delete.connect(object_deleted, ShowFeed, dispatch_uid="my_dispatch_uid")
        post_delete.connect(object_deleted, UserProfile, dispatch_uid="my_dispatch_uid")
        post_delete.connect(object_deleted, AuphonicSettings, dispatch_uid="my_dispatch_uid")


    def receive_messages(self):
        logger.info("Connecting to AMQP-Broker")
        conn = DjangoBrokerConnection()
        consumer = Consumer(connection=conn, queue="input", exchange="main", routing_key="#", exchange_type="topic")
        consumer.register_callback(process_message)
        import threading
        t = threading.Thread(target=consumer.wait)
        t.setDaemon(True)
        t.start()
