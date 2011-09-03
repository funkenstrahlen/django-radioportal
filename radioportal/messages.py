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
    )
    data = dto_serializer.serialize((instance,))
    publisher.send(data)
    publisher.close()                  
    print "Object delete message sent"

print "Connecting signals"

from radioportal.models import RecodedStream, SourcedStream, StreamSetup, ShowFeed, UserProfile
from django.db.models.signals import post_save, post_delete

post_save.connect(object_changed, RecodedStream, dispatch_uid="my_dispatch_uid")
post_save.connect(object_changed, SourcedStream, dispatch_uid="my_dispatch_uid")
post_save.connect(object_changed, StreamSetup, dispatch_uid="my_dispatch_uid")
post_save.connect(object_changed, ShowFeed, dispatch_uid="my_dispatch_uid")
post_save.connect(object_changed, UserProfile, dispatch_uid="my_dispatch_uid")

post_delete.connect(object_changed, RecodedStream, dispatch_uid="my_dispatch_uid")
post_delete.connect(object_changed, SourcedStream, dispatch_uid="my_dispatch_uid")
post_delete.connect(object_changed, StreamSetup, dispatch_uid="my_dispatch_uid")
post_delete.connect(object_changed, ShowFeed, dispatch_uid="my_dispatch_uid")
post_delete.connect(object_changed, UserProfile, dispatch_uid="my_dispatch_uid")



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


def process_message(message_data, message):
    message.ack()
    print "Received message: %s" % repr(message_data)
    obj = DTODeserializer(message_data)
    
    
    obj.save()
    #obj = json.Deserializer(message_data)
    #for o in obj:
    print "Parsed object: %s" % obj
    #obj = obj.next()
    
    
    #obj.save()
    
conn = DjangoBrokerConnection()
consumer = Consumer(connection=conn, queue="input", exchange="django", routing_key="input")
consumer.register_callback(process_message)
import threading
t = threading.Thread(target=consumer.wait)
t.setDaemon(True)
t.start()
