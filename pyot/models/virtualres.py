'''
Created on Jul 29, 2014

@author: andrea
'''

from django.db import models
import pickle
from rest import Resource
from django.db.models.signals import post_save
from django.dispatch import receiver
from pyot.vres.pf import apply_pf
from coapthon2.client.coap_protocol import HelperClient

DEF_VALUE_LENGTH = 1000

client = HelperClient()

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
        raise(NotImplementedError)
    def POST(self, name):
        raise(NotImplementedError)
    def PUT(self):
        raise(NotImplementedError)
    def DELETE(self):
        raise(NotImplementedError)
            
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


def client_callback(response):
    print 'Code == ', response.code
    if response.code != 65:
        print 'resource creation failed'


@receiver(post_save)
def pre_create_vr(sender, instance, **kwargs):
    # Returns false if 'sender' is NOT a subclass of AbstractModel
    if not issubclass(sender, VResource):
        return
    if kwargs['created'] == False:
        return
    print instance.uri    
    print "The vr is going to be created  *********************************\n\n"
    #r = Resource.objects.get(uri='/rd')
    path = instance.uri[1:]
    print "PATH ===================="  + path
    payload = instance.uri
    #from pyot.vres.vresApp import get_rd_host
    #rd_host = get_rd_host()
    client = HelperClient(server=("bbbb::1", 5683))
    function = client.protocol.post
    
    args = (path, payload)
    kwargs = {'Uri-Query':'pyot'}
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

    class Meta(object):
        app_label = 'pyot'

class VirtualSensorT(VResource):
    """
    TODO
    """
    def GET(self):
        """
        TODO
        """
        print "Periodic Virtual Sensor \n>> supported methods: \
GET|POST\n  >> Configuration\  >>   subresource: period\n>>   subresource: processing"
        return "virtual resource template sample"
    
    def POST(self, name):
        """
        Starting from the template creates the instance of the virtual 
        resource using the name provided by the user. If an instance having 
        that name is already existing it is returned to the user.
        """
        uri = str(self.uri + '/' + name)
        
        #print 'instance uri ===== ' + uri
        
        instance, created = VirtualSensorI.objects.get_or_create(template=self,
                                              host=self.host,
                                              uri=uri,
                                              title=name,
                                              rt=self.rt)
        
        period, _ = SubResource.objects.get_or_create(host=self.host,
                                uri=uri + '/period',
                                title='period',
                                rt=self.rt, 
                                defaults={'value':'60'})

        processing, _ = SubResource.objects.get_or_create(host=self.host,
                                uri=uri + '/processing',
                                title='processing',
                                rt=self.rt,
                                defaults={'value':None})
        if created is True:
            instance.period = period
            instance.processing = processing
            instance.save()


        return instance

    class Meta(object):
        app_label = 'pyot'




class VirtualActuatorT(VResource):
    """
    TODO
    """
    def GET(self):
        """
        TODO
        """
        return "virtual actuator template sample"
    
    def POST(self, name):
        """
        """
        uri = str(self.uri + '/' + name)
        #return instance

    class Meta(object):
        app_label = 'pyot'


class VirtualSensorI(VResource):
    """
    Virtual Resource Instance
    """
    #reference to the template so that we can get the input resource list
    template = models.ForeignKey(Resource, related_name='vs_template')
    period = models.ForeignKey(SubResource, related_name='period', null=True)
    processing = models.ForeignKey(SubResource, related_name='vs_processing', null=True) 
    
    class Meta(object):
        app_label = 'pyot'

    def GET(self):
        """
        Returns a list of values for each input sensor. Values are collected
        periodically.
        """
        print 'return the VALUE of the virtual resource'
        #print 'period =', self.period.GET()
        input_list = [1, 2, 3, 4, 5]
        output = apply_pf(self.processing.value, input_list)
        #for now we just return a fixed list of values
        return str(output)
        


class VirtualActuatorI(VResource):
    """
    Virtual Actuator Resource Instance
    """
    #reference to the template so that we can get the input resource list
    template = models.ForeignKey(Resource, related_name='va_template')
    
    class Meta(object):
        app_label = 'pyot'
    
    def PUT(self, value):
        pass
