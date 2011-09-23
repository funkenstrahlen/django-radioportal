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

#### Part one: sending notifications for changed objects ####

class DTOSerializer(json.Serializer):
    """
    Convert a queryset to JSON.
    """
    def end_serialization(self):
        self.objects = self.objects[0]
#        print "2, %s" % self.objects
        self.objects['fields']['pk'] = self.objects['pk']
#        print "3, %s" % self.objects
        self.objects['fields']['model'] = self.objects['model']
#        print "4, %s" % self.objects
        self.objects = self.objects['fields']
#        print "5, %s" % self.objects
        return json.Serializer.end_serialization(self)

dto_serializer = DTOSerializer()
#dto_serializer = json.Serializer()

def object_changed(sender, instance, created, **kwargs):
    conn = DjangoBrokerConnection()
    action = "created" if created else "changed"
    publisher = Publisher(connection=conn,
        exchange="django", 
    #    routing_key="%s.%s" % (sender._meta.verbose_name, action)
        exchange_type="topic",
    )
    data = dto_serializer.serialize((instance,))
    publisher.send(data) 
    publisher.close()                 
    print "Object change message sent"

def object_deleted(sender, instance, **kwargs):
    conn = DjangoBrokerConnection()
    publisher = Publisher(connection=conn,
        exchange="django", 
    #    routing_key="%s.deleted" % sender._meta.verbose_name
        exchange_type="topic",
    )
    data = dto_serializer.serialize((instance,))
    publisher.send(data)
    publisher.close()                  
    print "Object delete message sent"

from radioportal.models import RecodedStream, SourcedStream, StreamSetup, ShowFeed, UserProfile,\
        Episode, EpisodePart, Stream, Graphic, Recording


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
    def show_start(self, data):
        """
            value={'name': cpwd, 'time': int, 'show' : {'name': 'CR001 Titel der Sendung'}}
            FIXME: need show
        """
        data = simplejson.loads(data)
        setup = StreamSetup.objects.get(cluster=data['name'])
        if len(setup.show.all()) == 0:
            # FIXME
            print "no show"
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
            print "error"
            #FIXME

    def show_stop(self, data):
        """
            value={'name': cpwd}
        """
        data = simplejson.loads(data)
        print "in show_stop"
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
            print "no episode"
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
        
        stream = Stream.objects.get(setup__cluster=mount[0], format=mount[1].lower(), bitrate=int(mount[2]))
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
            print "key not in setup map"
         
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
        
        g.save()
        
    def recording_start(self, data):
        data = simplejson.loads(data)
        
        cpwd = data["cluster"]
        
        setup = StreamSetup.objects.get(cluster=cpwd)
        if setup.currentEpisode:
            part = setup.currentEpisode.current_part
        
        r = Recording(episode=part)
        r.path = data['path']
        r.format = data['format']
        r.bitrate = data['bitrate']
        r.size = 0
        r.running = True
        r.save()
    
    def recording_stop(self, data):
        data = simplejson.loads(data)
        cpwd = data["cluster"]
        setup = StreamSetup.objects.get(cluster=cpwd)
        if setup.currentEpisode:
            part = setup.currentEpisode.current_part
            rec = part.recordings.get(path=data['path'])
            rec.running = False
            rec.size = data['size']
            rec.save()


def process_message(message_data, message):
    try: 
        routing_key = message.delivery_info['routing_key']
        keys = routing_key.split(".", 1)
        if len(keys) != 2:
            print "routing_key %s to short" % routing_key
            message.ack()
            return
	print "calling bi.%s_%s(data)" % (keys[0], keys[1])
        
        bi = BackendInterpreter()
        if not hasattr(bi, '%s_%s' % (keys[0], keys[1])):
            print "no method for routing_key %s" % routing_key
            message.ack()
            return
        getattr(bi, '%s_%s' % (keys[0], keys[1]))(message_data)
    except Exception as inst:
        print "Exception: ", inst 
    message.ack()
    print "Received message: %s" % repr(message_data)
    #obj = DTODeserializer(message_data)
    
    
    #obj.save()
    #obj = json.Deserializer(message_data)
    #for o in obj:
    #print "Parsed object: %s" % obj
    #obj = obj.next()
    
    
    #obj.save()

class AMQPInitMiddleware(object):
    def __init__(self):
        print "in middleware"
#        self.send_messages()
        self.receive_messages()
        from django.core.exceptions import MiddlewareNotUsed
        raise MiddlewareNotUsed()

    def send_messages(self):
        print "Connecting signals"
        
        from django.db.models.signals import post_save, post_delete
        
        post_save.connect(object_changed, RecodedStream, dispatch_uid="my_dispatch_uid")
        post_save.connect(object_changed, SourcedStream, dispatch_uid="my_dispatch_uid")
        post_save.connect(object_changed, StreamSetup, dispatch_uid="my_dispatch_uid")
        post_save.connect(object_changed, ShowFeed, dispatch_uid="my_dispatch_uid")
        post_save.connect(object_changed, UserProfile, dispatch_uid="my_dispatch_uid")
        
        post_delete.connect(object_deleted, RecodedStream, dispatch_uid="my_dispatch_uid")
        post_delete.connect(object_deleted, SourcedStream, dispatch_uid="my_dispatch_uid")
        post_delete.connect(object_deleted, StreamSetup, dispatch_uid="my_dispatch_uid")
        post_delete.connect(object_deleted, ShowFeed, dispatch_uid="my_dispatch_uid")
        post_delete.connect(object_deleted, UserProfile, dispatch_uid="my_dispatch_uid")

    def receive_messages(self):
        print "Starting amqp-listener"
        conn = DjangoBrokerConnection()
        consumer = Consumer(connection=conn, queue="input", exchange="django", routing_key="#", exchange_type="topic")
        consumer.register_callback(process_message)
        import threading
        t = threading.Thread(target=consumer.wait)
        t.setDaemon(True)
        t.start()
