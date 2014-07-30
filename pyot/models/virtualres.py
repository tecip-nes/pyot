'''
Created on Jul 29, 2014

@author: andrea
'''

from django.db import models
import pickle
from rest import Resource

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

class SubResource(Resource):
    """
    TODO
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
GET|POST\n  >> Configuration\  >>   subresource: period"
    def POST(self, name):
        """
        TODO
        """
        uri = self.uri + '/' + name

        period = SubResource.objects.create(host=self.host,
                                uri=uri + '/period',
                                title='period',
                                rt=self.rt,
                                value='60')

        instance = PeriodicVsI.objects.create(template=self,
                                              host=self.host,
                                              uri=uri,
                                              title=name,
                                              rt=self.rt,
                                              period=period)

        return instance

    class Meta(object):
        app_label = 'pyot'


class PeriodicVsI(Resource):
    """
    TODO
    """
    #reference to the template so that we can get the input resource list
    template = models.ForeignKey(Resource, related_name='template')
    period = models.ForeignKey(SubResource, related_name='period')

    class Meta(object):
        app_label = 'pyot'

    def GET(self):
        """
        Returns a list of values for each input sensor. Values are collected
        periodically.
        """
        print 'return the VALUE of the virtual resource'
        print 'period =', self.period.GET()
        

from django.db.models.signals import post_save
       
def periodic_instance_created(sender, **kwargs):
    print "The instance has been saved in the db, time to deploy!"
    print "activate a task which get the value from the input set with the specified period"
    print "the task could be deployed in-network or as a simple process on the pyot node"       


post_save.connect(periodic_instance_created, 
                  dispatch_uid="my_unique_identifier", sender=PeriodicVsI)













