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

from vresbase import SubResource, VResource, DEF_PF
from pyot.vres.pf import apply_pf
from django.db import models
from pyot.models.rest import Resource, CoapMsg
from datetime import datetime, timedelta
from calendar import timegm

class VirtualSensorHistT(VResource):
    """
    TODO
    """
    
    default_pf = DEF_PF
    
    def GET(self):
        """
        TODO
        """
        print "Past virtual sensor \nSubresources: \n  -processing \n  -startTime \n  -endTime"
        return "virtual resource Past sensor template"
    
    def POST(self, name):
        """
        Starting from the template creates the instance of the virtual 
        resource using the name provided by the user. If an instance having 
        that name is already existing it is returned to the user.
        """
        uri = str(self.uri + '/' + name)
        
        instance, created = VirtualSensorHistI.objects.get_or_create(template=self,
                                              host=self.host,
                                              uri=uri,
                                              title=name,
                                              rt=self.rt)

        processing, _ = SubResource.objects.get_or_create(host=self.host,
                                    uri=uri + '/proc',
                                    title='processing',
                                    rt=self.rt, 
                                    defaults={'value':self.default_pf})

        yesterday = datetime.now() - timedelta(days=1)
        yesterday_unix = str(timegm(yesterday.timetuple()))
        start, _ = SubResource.objects.get_or_create(host=self.host,
                                    uri=uri + '/start',
                                    title='start',
                                    rt=self.rt, 
                                    defaults={'value':yesterday_unix})
        
        
        now_unix = str(timegm(datetime.now().timetuple()))
        
        end, _ = SubResource.objects.get_or_create(host=self.host,
                                    uri=uri + '/end',
                                    title='end',
                                    rt=self.rt, 
                                    defaults={'value':now_unix})        
        
        if created is True:
            instance.processing = processing
            instance.start_time = start
            instance.end_time = end
            instance.save()
        return instance

    class Meta(object):
        app_label = 'pyot'
        
        
class VirtualSensorHistI(VResource):
    """
    Virtual Resource Instance
    """
    #reference to the template so that we can get the input resource list
    template = models.ForeignKey(Resource, related_name='vsh_template')
    processing = models.ForeignKey(SubResource, 
                                   related_name='vsh_processing', 
                                   null=True, 
                                   on_delete=models.SET_NULL) 

    start_time = models.ForeignKey(SubResource, 
                                   related_name='vsh_start', 
                                   null=True, 
                                   on_delete=models.SET_NULL) 

    end_time = models.ForeignKey(SubResource, 
                                   related_name='vsh_end', 
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
        ress =  self.template.get_io_resources()
        messages = CoapMsg.objects.filter(resource__in=ress)
        print 'before filtering', messages.count()         
        start = datetime.fromtimestamp(int(self.start_time.value))
        endtime = datetime.fromtimestamp(int(self.end_time.value))  
        messages.filter(timeadded__gte=start).filter(timeadded__lte=endtime)
        print 'after filtering', messages.count()                                    
        # query the db
        #active_ress = ress.filter(host__active=True)
        #for i in active_ress:
        #    resp = i.GET()
        #    input_list.append(int(resp.content))
        input_list = [int(x.payload) for x in messages]
        output, _ = apply_pf(self.processing.value, input_list)
        return str(output)     
