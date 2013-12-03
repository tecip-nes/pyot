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
import networkx as nx
from networkx import *
import pickle

class RplGraph(models.Model):
    _graph = models.CharField(max_length=1000, blank=True, null=True)
    def set_data(self, G):
        self._graph = pickle.dumps(G)
    def get_data(self):
        return pickle.loads(self._graph)
    graph = property(get_data, set_data)    

    class Meta:
        app_label = 'pyot'
    def getGrapg(self):
        return self.graph
    def getPNG(self):
        pass    
