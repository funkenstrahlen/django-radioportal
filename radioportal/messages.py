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
import radioportal

import logging

logger = logging.getLogger(__name__)

from radioportal.models import RecodedStream, SourcedStream, StreamSetup, ShowFeed, UserProfile,\
        Episode, EpisodePart, Stream, Graphic, Recording

#### Part one: sending notifications for changed objects ####

class DTO(object):
    def serialize(self):
        return simplejson.dumps(self.__dict__)

class DTOSourcedStream(DTO):
    def __init__(self, instance):
        self.mount = instance.mount
        self.user = instance.user
        self.password = instance.password
        self.encoding = instance.encoding
        self.cluster = instance.setup.cluster
        self.id = instance.id

class DTOShowFeed(DTO):
    def __init__(self, instance):
        self.enabled = instance.enabled
        self.feed = instance.feed
        self.title_regex = instance.titlePattern
        self.show = instance.show.slug

class DTOUserProfile(DTO):
    def __init__(self, instance):
        self.id = instance.id
        self.htdigest = instance.htdigest

class DTOSerializer(object):
    def serialize(self, instance):
        if instance._meta.object_name == "SourcedStream":
            return DTOSourcedStream(instance).serialize()
        elif instance._meta.object_name == "ShowFeed":
            return DTOShowFeed(instance).serialize()
        elif instance._meta.object_name == "UserProfile":
            return DTOUserProfile(instance).serialize()
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

class BackendInterpreter(object):
    def show_startmaster(self, data):
        """
            value={'name': cpwd, 'time': int, 'show' : {'name': 'CR001 Titel der Sendung'}}
            FIXME: need show
        """
        data = simplejson.loads(data)
        setup = StreamSetup.objects.get(cluster=data['name'])
        if len(setup.show.all()) == 0:
            logger.error("show_startmaster: No show found for cluster %s" % data['name'])
            # FIXME
            return

        # take the first show available
        show = setup.show.all()[0]
        
        # Guess episode name from stream metadata
        episode_slug = data['show']['name'].split(" ")[0].lower()
        episode = Episode.objects.filter(show=show, slug=episode_slug)
        if len(episode) == 1:
            episode = episode[0]
            
            if episode.status == Episode.STATUS[2][0]:
                part = episode.parts.all().reverse()[0]
            else:
                part = EpisodePart(episode=episode)

            part.begin = datetime.now()
            part.save()                

            episode.status = "RUNNING"
            episode.current_part = part
            episode.save()

            setup.currentEpisode = episode
            setup.save()
        elif len(episode) == 0:
            show.nextEpisodeNumber += 1
            show.save()
            
            episode_slug = "%s%03i" % (show.defaultShortName, 
                            show.nextEpisodeNumber)
            episode = Episode(show=show, slug=episode_slug)
            episode.status = "RUNNING"
            episode.save()
           
            setup.currentEpisode = episode
            setup.save()
 
            part = EpisodePart(episode=episode)
            part.begin = datetime.now()
            part.save()
            
            episode.current_part = part
            episode.save()
        else:
            logger.error("More than one episode found for show %s and episode slug %s" % (show.slug, episode_slug))
            #FIXME

    def show_stop(self, data):
        """
            value={'name': cpwd}
        """
        data = simplejson.loads(data)
        setup = StreamSetup.objects.get(cluster=data['name'])
        if setup.currentEpisode:
            episode = setup.currentEpisode 
            part = episode.current_part
            part.end = datetime.now()
            part.save()
            episode.current_part = None
            episode.status = Episode.STATUS[0][0]
            episode.save()
            setup.currentEpisode = None
            setup.save()
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
            setup = StreamSetup.objects.get(cluster=data['name'].split("-")[0])
            stream = Stream(mount=mp, setup=setup)
        stream.running = True
        stream.bitrate = data['stream']['bitrate']
        stream.format = data['stream']['type'].lower()
        stream.save()
        #stream.setup.updateRunning()
        
    def stream_stop(self, data):
        """
            value={'name': mount}
        """
        data = simplejson.loads(data)
        mount = data['name'].split("-")
        
        stream = Stream.objects.get(setup__cluster=mount[0], format=mount[2].lower(), bitrate=int(mount[1]))
        stream.running = False
        stream.save()

    def show_metadata(self, data):
        """
            value={'name': mount, 'key': key, 'val': val}
        """
        data = simplejson.loads(data)
        
        setup = StreamSetup.objects.get(cluster=data['name'].split("-")[0])
        
        # mapping internal keys to attributes of stream setup
        map2setup={'name': 'streamShow','genre':'streamGenre',
             'current_song': 'streamCurrentSong',
             'description':'streamDescription', 'url': 'streamURL'}
        if data['key'] in map2setup:
            setattr(setup, map2setup[data['key']], data['val'])
            setup.save()
        else:
            logger.debug("show_metadata: key %s not in setup map" % data['key'])
         
        # mapping between internal keys and episode fields
        map2eps={'name': 'title', 'description': 'description', 'url': 'url'}
        
        if setup.currentEpisode:
            episode = setup.currentEpisode
            part = episode.current_part
            if data['key'] == 'name' and data['val'].lower().startswith(episode.slug):
                data['val'] = data['val'][len(episode.slug):].strip()
            if data['key'] in map2eps:
                setattr(part, map2eps[data['key']], data['val'])
                part.save()
        else:
            logger.error("show_metadata: no current episode for %s" % setup.cluster)
        
    def graphic_created(self, data):
        """
            value={'show': show, 'file': name})
        """
        data = simplejson.loads(data)
        
        cpwd = data['show'].split("-")[0]
        setup = StreamSetup.objects.get(cluster=cpwd)
        
        g = Graphic(file='graphics/%s' % data['file'])
        
        if setup.currentEpisode:
            g.episode = setup.currentEpisode.current_part
        else:
            logger.error("graphic_create: no current episode for %s" % setup.cluster)
        
        g.save()
        
    def recording_start(self, data):
        data = simplejson.loads(data)
        
        cpwd = data["cluster"]
        
        setup = StreamSetup.objects.get(cluster=cpwd)
        if setup.currentEpisode:
            part = setup.currentEpisode.current_part
        else:
            logger.error("recording_start: no current episode for %s" % setup.cluster)
       
        r = Recording(episode=part)
        r.path = data['file']
        r.format = data['format']
        r.bitrate = data['bitrate']
        r.size = 0
        r.running = True
        r.save()
    
    def recording_stop(self, data):
        data = simplejson.loads(data)
        rec = Recordings.objects.get(path=data['file'])
        rec.running = False
        rec.size = data['size']
        rec.save()


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
        getattr(bi, '%s_%s' % (keys[0], keys[1]))(message_data)
    except Exception as inst:
        logger.exception(inst)
    message.ack()
    logger.debug("Received message: %s" % repr(message_data))
    #obj = DTODeserializer(message_data)
    
    
    #obj.save()
    #obj = json.Deserializer(message_data)
    #for o in obj:
    #print "Parsed object: %s" % obj
    #obj = obj.next()
    
    
    #obj.save()

class AMQPInitMiddleware(object):
    def __init__(self):
        logger.info("Loading AMQP Middleware")
        self.send_messages()
        self.receive_messages()
        from django.core.exceptions import MiddlewareNotUsed
        raise MiddlewareNotUsed()

    def send_messages(self):
        logger.info("Connecting model change signals to amqp")
        
        from django.db.models.signals import post_save, post_delete
        
        post_save.connect(object_changed, RecodedStream, dispatch_uid="my_dispatch_uid")
        post_save.connect(object_changed, SourcedStream, dispatch_uid="my_dispatch_uid")
        #post_save.connect(object_changed, StreamSetup, dispatch_uid="my_dispatch_uid")
        post_save.connect(object_changed, ShowFeed, dispatch_uid="my_dispatch_uid")
        post_save.connect(object_changed, UserProfile, dispatch_uid="my_dispatch_uid")
        
        post_delete.connect(object_deleted, RecodedStream, dispatch_uid="my_dispatch_uid")
        post_delete.connect(object_deleted, SourcedStream, dispatch_uid="my_dispatch_uid")
        #post_delete.connect(object_deleted, StreamSetup, dispatch_uid="my_dispatch_uid")
        post_delete.connect(object_deleted, ShowFeed, dispatch_uid="my_dispatch_uid")
        post_delete.connect(object_deleted, UserProfile, dispatch_uid="my_dispatch_uid")

    def receive_messages(self):
        logger.info("Connecting to AMQP-Broker")
        conn = DjangoBrokerConnection()
        consumer = Consumer(connection=conn, queue="input", exchange="main", routing_key="#", exchange_type="topic")
        consumer.register_callback(process_message)
        import threading
        t = threading.Thread(target=consumer.wait)
        t.setDaemon(True)
        t.start()
