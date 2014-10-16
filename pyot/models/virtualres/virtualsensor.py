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
from vresbase import SubRes, VResource, DEF_PF


class VsT(VResource):
    """
    TODO
    """

    default_pf = DEF_PF

    def GET(self):
        """
        TODO
        """
        print "Virtual Sensor \n>> supported methods: \
GET|POST\n  >> Configuration\  >>   subresource: period\n>>\
subresource: processing"
        return "virtual sensor template"

    def POST(self, name):
        """
        Starting from the template creates the instance of the virtual
        resource using the name provided by the user. If an instance having
        that name is already existing it is returned to the user.
        """
        uri = str(self.uri + '/' + name)

        # print 'instance uri ===== ' + uri

        instance, created = VsI.objects.get_or_create(template=self,
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

        # except Exception as e:
        #    print 'error creating subresource: %s' % e

        if created is True:
            instance.processing = processing
            instance.save()
        return instance

    class Meta(object):
        app_label = 'pyot'


class VsI(VResource):
    """
    Virtual Resource Instance
    """
    # reference to the template so that we can get the input resource list
    template = models.ForeignKey(Resource, related_name='vs_template')
    # period = models.ForeignKey(SubRes, related_name='period', null=True)
    processing = models.ForeignKey(SubRes,
                                   related_name='vs_processing',
                                   null=True,
                                   on_delete=models.SET_NULL)

    class Meta(object):
        app_label = 'pyot'

    def GET(self):
        """
        get current values from input sensors, apply the processing function
        on the input list and return the result.
        """
        print self.template.ioSet
        input_list = []
        ress = self.template.get_io_resources()
        active_ress = ress.filter(host__active=True)
        for i in active_ress:
            resp = i.GET()
            input_list.append(int(resp.content))

        output, _ = apply_pf(self.processing.value, input_list)
        return str(output)
