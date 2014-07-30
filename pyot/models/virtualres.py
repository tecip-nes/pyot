'''
Created on Jul 29, 2014

@author: andrea
'''

from django.db import models
import pickle
from rest import Resource


class VResource(Resource):
    """
    Abstract base class for virtual sensors and actuators templates.
    """
    _inputSet = models.CharField(max_length=1000, blank=True, null=True)

    def set_data(self, inputSet):
        self._inputSet = pickle.dumps(inputSet)
    def get_data(self):
        return pickle.loads(self._inputSet)

    inputSet = property(get_data, set_data)

    def GET(self):
        print 'virtual GET'
    def POST(self, name):
        print 'virtual POST' + name

    class Meta(object):
        app_label = 'pyot'
        abstract = True


class PeriodicVsT(VResource):
    """
    TODO
    """
    rt = 'virtual'
    def GET(self):
        print 'supported methods: GET\nsubresource: period'
    def POST(self, name):
        uri = self.uri + '/' + name

        period = Resource.objects.create(host=self.host,
                                uri=uri + '/period',
                                title='period',
                                rt=self.rt)

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
    template = models.ForeignKey(Resource, related_name='template')
    period = models.ForeignKey(Resource, related_name='period')
    periodValue = models.IntegerField(default=60)
    #reference to the template so that we can get the input resource list
    class Meta(object):
        app_label = 'pyot'

    def GET(self):
        print 'return the VALUE of the virtual resource'
