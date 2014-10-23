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

from pyot.models.rest import Resource
from pyot.vres.pf import apply_pf
from vresbase import SubRes, VResource, DEF_PF, DEF_VALUE_LENGTH
from pyot.tres.tresApp import *
from pyot.models.tres import TRES_STATES


class VsPeriodicT(VResource):
    """
    TODO
    """

    default_pf = DEF_PF
    default_period = '60'

    def GET(self):
        """
        TODO
        """
        print "Periodic Virtual Sensor \n>> supported methods: \
GET|POST\n  >> Configuration\  >>   subresource: period\n>>   \
subresource: processing"
        return "virtual sensor periodic template"

    def POST(self, name):
        """
        Starting from the template creates the instance of the virtual
        resource using the name provided by the user. If an instance having
        that name is already existing it is returned to the user.
        """
        uri = str(self.uri + '/' + name)

        # print 'instance uri ===== ' + uri

        instance, created = VsPeriodicI.objects.get_or_create(template=self,
                                                              host=self.host,
                                                              uri=uri,
                                                              title=name,
                                                              rt=self.rt)

        processing, _ = SubRes.objects.get_or_create(host=self.host,
                                                     uri=uri + '/proc',
                                                     title='processing',
                                                     rt=self.rt,
                                                     defaults={'value':
                                                               self.default_pf})

        period, _ = SubRes.objects.get_or_create(host=self.host,
                                                 uri=uri + '/period',
                                                 title='period',
                                                 rt=self.rt,
                                                 defaults={'value':
                                                           self.default_period})

        last_value, _ = SubRes.objects.get_or_create(host=self.host,
                                                     uri=uri + '/lo',
                                                     title='lastvalue',
                                                     rt=self.rt,
                                                     defaults={'value': 'None'})

        if created is True:
            instance.processing = processing
            instance.period = period
            instance.last_value = last_value
            instance.save()

        return instance

    class Meta(object):
        app_label = 'pyot'


class VsPeriodicI(VResource):
    """
    Virtual Resource Instance.
    When the T-Res task is installed and activated it subscribes to
    the input sources and will update the output destination (i.e., the
    virtual sensor instance, with the defined period.
    Note: the processing function in this case MUST adhere to the T-Res API
    """
    # reference to the template so that we can get the input resource list
    template = models.ForeignKey(Resource, related_name='vsp_template')
    period = models.ForeignKey(SubRes, related_name='vsp_period',
                               null=True)
    processing = models.ForeignKey(SubRes,
                                   related_name='vsp_processing',
                                   null=True,
                                   on_delete=models.SET_NULL)
    last_value = models.ForeignKey(SubRes, related_name='vsp_last',
                                   null=True)

    tresTask = models.ForeignKey(TResT, null=True,
                                 related_name='vsp_tresTasks')

    class Meta(object):
        app_label = 'pyot'

    def GET(self):
        """
        Return the internal value of the virtual resource. The value should
        be updated by the processing node.
        """
        if self.last_value:
            return Resource.objects.get(uri=self.last_value.uri).GET()
        else:
            return 'None'

    def PUT(self, value):
        """
        Deploy and activate the task
        Create the appropriate t-res instance, deploy it and start it.
        The input sources are defined starting from the resource template.
        The output destination resource is the instance itself.
        In case in-network processing is not possible (maybe there's no
        t-res node available) we can use the 'emulate' function to run the
        processing function on the worker node (though periodicity is still
        not supported)
        """
        print 'put'

        if self.tresTask is not None:
            print 'stopping'
            self.tresTask.stop()
            self.tresTask.uninstall()
            self.last_value.value = None
            self.tresTask = None
            self.save()
            print 'removed'
            return 'task removed'

        print 'deploying task'

        proc = TResPF.fromSource(self.processing.value, 'vr_proc')
        rin = Resource.objects.filter(**self.template.ioSet)
        rout = Resource.objects.filter(uri=self.last_value.uri)[0]

        print rin, rout

        task = TResT.objects.create(pf=proc.pf, period=self.period.value)
        task.output.add(rout)

        for inp in rin:
            task.inputS.add(inp)
        task.save()

        self.tresTask = task
        self.save()
        r = Resource.objects.filter(uri='/tasks')[0]  # pick a t-res node
        print r.host, '    is a t-res node'
        self.tresTask.deploy(r)

        r = self.tresTask.start()

        return 'resource updated'
