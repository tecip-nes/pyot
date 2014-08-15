'''
Created on Jul 29, 2014

@author: andrea
'''

from django.db import models
import pickle
from rest import Resource
from django.db.models.signals import post_save, pre_save, post_init
from django.dispatch import receiver
from twisted.internet import reactor

DEF_VALUE_LENGTH = 1000

class VResource(Resource):
    """
    Abstract base class for virtual sensors and actuators templates.
    """
    _ioSet = models.CharField(max_length=DEF_VALUE_LENGTH, blank=True, null=True)
    rt = 'virtual'        
    def set_data(self, ioSet):
        self._ioSet = pickle.dumps(ioSet)
    def get_data(self):
        return pickle.loads(self._ioSet)

    ioSet = property(get_data, set_data)

    def GET(self):
        print 'virtual GET'
    def POST(self, name):
        print 'virtual POST' + name

    def get_io_resources(self):
        """
        Returns a queryset including the current list of input/output
        relevant resources, based on the resource template. 
        """
        kwparams = self.ioSet
        return Resource.objects.filter(**kwparams)

    class Meta(object):
        app_label = 'pyot'
        abstract = True

from coapthon2.client.coap_protocol import HelperClient

client = HelperClient()

def client_callback(response):
    pass

import sys


@receiver(post_save)
def pre_create_vr(sender, instance, **kwargs):
    # Returns false if 'sender' is NOT a subclass of AbstractModel
    if not issubclass(sender, VResource):
       return
    if kwargs['created'] == False:
        return
    print instance.uri    
    print "The vr is going to be created  *********************************\n\n"
    #from pyot.resourceDirectory import Vr, CoAPServer
    #rd = CoAPServer("[bbbb::1]", 5683)
    #rd.add_resource(instance.uri, Vr())
    r = Resource.objects.get(uri='/rd')
    #r.POST(payload=instance.uri)
    #path = 'rd' + '/' + instance.uri[1:]
    path = instance.uri[1:]
    
    print "PATH ===================="  + path
    sys.stdout.flush()
    payload = instance.uri
    client = HelperClient(server=("bbbb::1", 5683))
    function = client.protocol.post
    args = (path, payload)
    kwargs = {}
    callback = client_callback
    operations = [(function, args, kwargs, callback)]
    try:
        client.start(operations)
    except:
        client.add_operations(operations)    
    
class SubResource(VResource):
    """
    Configuration Resources for Virtual Sensors/actuators instances. Their value 
    is directly encoded in the resource directory (--> db) as a string. 
    """
    value = models.CharField(max_length=DEF_VALUE_LENGTH, blank=True, null=True)

    def GET(self):
        print 'virtual GET'
        return self.value
    
    def PUT(self, newvalue):
        print 'virtual PUT'
        self.value = newvalue
        self.save()
        
    def POST(self, newvalue):
        print 'virtual POST'
        self.value = newvalue
        self.save()

    class Meta(object):
        app_label = 'pyot'

class PeriodicVsT(VResource):
    """
    TODO
    """
    def GET(self):
        """
        TODO
        """
        print "Periodic Virtual Sensor \n>> supported methods: \
GET|POST\n  >> Configuration\  >>   subresource: period\n>>   subresource: processing"
    def POST(self, name):
        """
        TODO
        """
        uri = str(self.uri + '/' + name)
        print 'instance uri ===== ' + uri
        instance = PeriodicVsI.objects.create(template=self,
                                              host=self.host,
                                              uri=uri,
                                              title=name,
                                              rt=self.rt)
        
        period = SubResource.objects.create(host=self.host,
                                uri=uri + '/period',
                                title='period',
                                rt=self.rt,
                                value='60')

        processing = SubResource.objects.create(host=self.host,
                                uri=uri + '/processing',
                                title='processing',
                                rt=self.rt,
                                value=None)
        instance.period = period
        instance.processing = processing
        instance.save()


        return instance

    class Meta(object):
        app_label = 'pyot'

proc="""
print 'this is a user-defined processing function'
"""


def apply_pf(pf, input_list):
    pass

class PeriodicVsI(VResource):
    """
    TODO
    """
    #reference to the template so that we can get the input resource list
    template = models.ForeignKey(Resource, related_name='template')
    period = models.ForeignKey(SubResource, related_name='period', null=True)
    processing = models.ForeignKey(SubResource, related_name='processing', null=True) 
    
    class Meta(object):
        app_label = 'pyot'

    def GET(self):
        """
        Returns a list of values for each input sensor. Values are collected
        periodically.
        """
        print 'return the VALUE of the virtual resource'
        print 'period =', self.period.GET()
        
        #for now we just return a fixed list of values
        return [1, 2, 3, 4, 5]
        


       
def periodic_instance_created(sender, instance, **kwargs):
    #print instance.template.ioSet
    pass

post_save.connect(periodic_instance_created, 
                  dispatch_uid="my_unique_identifier", sender=PeriodicVsI)


