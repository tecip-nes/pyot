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
from models.rpl import *

#import matplotlib.pyplot as plt
import networkx as nx
#import matplotlib.image as mpimg


def searchHost(eui, network):
    from models import Host
    h = Host.objects.filter(kqueue=network)
    for i in h:
        if i.ip6address.exploded[20:].replace(':','') == eui:
            return i.ip6address.exploded[-5:]
    return '6LBR'

def DAGupdate(Net):
    from models import Resource, RplGraph, Network
    G=nx.DiGraph(directed=True)

    parents = Resource.objects.filter(uri='/rplinfo/parents', host__active=True, host__kqueue=Net)
    import json
    for p in parents:
        print 'Searching parents for resource: ', p
        pNumber = p.GET()
        #print 'Searching parents for resource: ', p, pNumber
        
        for index in range(int(pNumber)):
            prefix = p.GET(query='index='+str(index))
            l = json.loads(prefix)
            pa = searchHost(l['eui'], Net)
            G.add_edge(p.host.ip6address.exploded[-5:], pa)
    graph = RplGraph.objects.create(graph=G, net=Net)
    return graph


    
    
    