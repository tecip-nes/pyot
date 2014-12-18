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
import json

import networkx as nx
from pyot.models.rest import Resource, CONTENT
from pyot.models.rpl import RplGraph, search_host, short_name


def DAGupdate(network):
    G = nx.DiGraph(directed=True)

    parents = Resource.objects.filter(uri='/rplinfo/parents',
                                      host__active=True, host__network=network)
    for parent in parents:
        print 'Searching parents for resource: ', parent
        # with the current implementation nodes have only one parent, index=0
        r = parent.GET(query='index=0')
        if r.code != CONTENT:
            continue
        print r.content
        prefix = r.content
        l = json.loads(prefix)
        pa = search_host(l['eui'], network)
        G.add_edge(short_name(parent.host), pa)
    graph = RplGraph.objects.create(graph=G.reverse(), net=network)
    return graph
