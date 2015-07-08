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
from django.template import Context

from pyot.models import EventHandler


class GenericResource(object):
    template = 'resource.htm'

    def __init__(self, rid):
        self.c = {'rid': rid.id,
                  'uri': rid.uri,
                  'ip': rid.host.ip6address,
                  'hid': rid.host.id}

    def getTemplate(self, request):
        return Context(self.c), self.template


class ObservableResource(GenericResource):
    template = 'observable_template.htm'

    def __init__(self, rid):
        GenericResource.__init__(self, rid)
        try:
            handlers = EventHandler.objects.filter(active=True)
        except Exception:
            handlers = None
        c2 = {'handlers': handlers}
        self.newContext = dict(self.c.items() + c2.items())

    def getTemplate(self, request):
        return Context(self.newContext), self.template


def getRenderer(rid):
    if rid.obs:
        return ObservableResource(rid)
    else:
        return GenericResource(rid)

