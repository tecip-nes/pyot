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
import errno
from networkx import *
import os
import pickle
from django.db.models.query import QuerySet
from rest import Network, Host
from settings import MEDIA_ROOT


fmt = "%Y%m%d%H%M%S"
BASE_PATH = MEDIA_ROOT + 'rpl/'

def shortName(ip):
    return ip.ip6address.exploded[-5:]

def searchHost(eui, network):
    from pyot.models.rest import Host
    h = Host.objects.filter(kqueue=network)
    for i in h:
        if i.ip6address.exploded[20:].replace(':','') == eui:
            return i.ip6address.exploded[-5:]
    return '6LBR'

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

class RplGraph(models.Model):
    _graph = models.CharField(max_length=5000, blank=True, null=True)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)
    net = models.ForeignKey(Network)    
    def set_data(self, G):
        self._graph = pickle.dumps(G)
    def get_data(self):
        return pickle.loads(self._graph)
    graph = property(get_data, set_data)    

    class Meta:
        app_label = 'pyot'
    def __unicode__(self):
        return u"Rpl graph for %s" % (self.net.hostname) #TODO: more specific info      
     
    def getPNG(self, highlight_list=None, color='red'):
        
        A=to_agraph(self.graph)
        
        if highlight_list :
            if isinstance(highlight_list,Host):
                s = shortName(highlight_list)
                try:
                    A.nodes()[A.nodes().index(s)].attr['color'] = color
                except Exception:
                    pass
            elif isinstance(highlight_list,QuerySet):
                for n in highlight_list:
                    s = shortName(n)
                    try:
                        A.nodes()[A.nodes().index(s)].attr['color'] = color
                    except Exception:
                            pass                    
        
        
        ts = self.timeadded.strftime(fmt)
        #TODO: assicurare la presenza della directory
        dir_ = BASE_PATH +self.net.hostname + '/'
        make_sure_path_exists(dir_)
        path =  dir_ + 'rpl'+ts+'.png'
        A.layout(prog='dot') 
        A.draw(path, format='png')
        return path   
    