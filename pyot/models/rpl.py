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

import errno
import os
import pickle

from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from networkx import to_agraph
from networkx.algorithms import ancestors, descendants, shortest_path_length

import rest


MEDIA_ROOT = settings.MEDIA_ROOT
FMT = "%Y%m%d%H%M%S"
BASE_PATH = MEDIA_ROOT + 'rpl/'


def short_name(host):
    '''
    Returns a more compact (but incomplete) representation of an IPv6
    address (last 5 digits). It is used to label the nodes in the
    graph.
    '''
    return host.ip6address.exploded[-5:]


def search_host(eui, network):
    '''
    Returns the short name (short ip) address of a node in the network (the
    network uses the MAC address of the nodes).
    '''
    hosts = rest.Host.objects.filter(network=network)
    for i in hosts:
        if i.ip6address.exploded[20:].replace(':', '') == eui:
            return short_name(i)
    return '6LBR'


def make_sure_path_exists(path):
    '''
    Checks if a path exists in the file system.
    '''
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


class RplGraph(models.Model):
    '''
    Representation of a RPL graph, based on networkX serialized objects.
    '''
    _graph = models.CharField(max_length=5000, blank=True, null=True)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)
    net = models.ForeignKey(rest.Network)

    def set_data(self, graph):
        self._graph = pickle.dumps(graph)

    def get_data(self):
        return pickle.loads(self._graph)
    graph = property(get_data, set_data)

    class Meta(object):
        app_label = 'pyot'

    def __unicode__(self):
        return u"Rpl graph for %s" % (self.net.hostname) # TODO: be more specific

    def getGraph(self):
        return self.graph

    def getPNG(self, highlight_list=None, color='red'):
        A = to_agraph(self.graph)

        if highlight_list:
            if isinstance(highlight_list, rest.Host):
                s = short_name(highlight_list)
                try:
                    A.nodes()[A.nodes().index(s)].attr['color'] = color
                except Exception:
                    pass
            elif isinstance(highlight_list, QuerySet):
                for n in highlight_list:
                    s = short_name(n)
                    try:
                        A.nodes()[A.nodes().index(s)].attr['color'] = color
                    except Exception:
                        pass
        ts = self.timeadded.strftime(FMT)
        dir_ = BASE_PATH + self.net.hostname + '/'
        make_sure_path_exists(dir_)
        path = dir_ + 'rpl' + ts + '.png'
        A.layout(prog='dot')
        A.draw(path, format='png')
        return path

    def find_node_from_host(self, host):
        nodes = self.graph.nodes()
        for n in nodes:
            if short_name(host) == n:
                return n

    def find_host_from_node(self, node):
        hosts = rest.Host.objects.filter(network=self.net)
        for host in hosts:
            if node == short_name(host):
                return host
        return None

    def get_ancestors(self, host):
        node = self.find_node_from_host(host)
        if node:
            return ancestors(self.graph, node)
        else:
            return []

    def get_descendants(self, host):
        node = self.find_node_from_host(host)
        if node:
            return descendants(self.graph, node)
        else:
            return []

    def get_shortest_path_length(self, host):
        node = self.find_node_from_host(host)
        if node in self.graph.nodes():
            return shortest_path_length(self.graph, node, '6LBR')
