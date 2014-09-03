'''
Copyright (C) 2012,2013 Scuola Superiore Sant'Anna (http://www.sssup.it)
and Consorzio Nazionale Interuniversitario per le Telecomunicazioni
(http://www.cnit.it).

This file is part of PyoT, an IoT Django-based Macroprogramming Environment.

PyoT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyoT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyoT.  If not, see <http://www.gnu.org/licenses/>.

@author: Andrea Azzara' <a.azzara@sssup.it>
'''

from django.db import models
import pickle
from pyot.models.rest import Resource
from django.db.models.signals import post_save
from django.dispatch import receiver

DEF_VALUE_LENGTH = 1000

DEF_PF = "print 'please, specify a pf'"


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


@receiver(post_save)
def pre_create_vr(sender, instance, **kwargs):
    """
    TODO
    """
    # Returns false if 'sender' is NOT a subclass of AbstractModel
    if not issubclass(sender, VResource):
        return
    if kwargs['created'] == False:
        return
    print instance.uri    
    print "The vr is going to be created  *********************************\n\n"
    from pyot.tasks import coapPost
    res = coapPost(ip6address="bbbb::1", uri=instance.uri, payload = instance.uri, timeout=30)
    if res.code != '2.01':
        raise Exception("could not create resource in rd")
    
    
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
        