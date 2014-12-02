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
from pyot.tres.tresApp import TResPF
from pyot.models.mapreduce import pyMap, pyMapReduce

class pMap(object):
    """
    Programmer interface to create a PyoT Map task. Map is
    realized using CoAP REST interface. The resources must
    support Observe option.
    """
    mapId = None
    def __init__(self, inputS, name='map', period=0):
        #check if the input resource list is empty
        if inputS.count() == 0:
            raise Exception('Empty input resource list')
        #First check if input resources are observable
        for inp in inputS:
            if inp.obs == False:
                raise Exception('Input resources must be observable')
        pymap = pyMap.objects.create(name=name, period=period)
        self.mapId = pymap.id
        for inp in inputS:
            pymap.inputS.add(inp)
        pymap.save()

    def getMapObject(self):
        return pyMap.objects.get(id=self.mapId)

    def __repr__(self):
        t = self.getMapObject()
        return t.__unicode__()


class pReduce(TResPF):
    """
    Programmer interface to create a PyoT Reduce task. Just another 
    name for a T-Res processing function.
    """
    pass


class pMapReduce(object):
    """
    Programmer interface to create a PyoT MapReduce task.
    """
    mapReduceId = None
    def __init__(self, pmap, preduce, output, min_input=2):
        #check argument types
        if not isinstance(pmap, pMap):
            raise Exception("Wrong type for pMap argument")
        if not isinstance(preduce, pReduce):
            raise Exception("Wrong type for pReduce argument")

        pymr = pyMapReduce.objects.create(pmap=pmap.getMapObject(),
                                          preduce=preduce.pf,
                                          output=output,
                                          min_input=min_input)
        self.mapReduceId = pymr.id

    def getMapReduceObject(self):
        return pyMapReduce.objects.get(id=self.mapReduceId)

    def __repr__(self):
        t = self.getMapReduceObject()
        return t.__unicode__()

    def deploy(self, Network):
        t = self.getMapReduceObject()
        return t.deploy(Network)

    def start(self):
        t = self.getMapReduceObject()
        return t.start()

    def stop(self):
        t = self.getMapReduceObject()
        return t.stop()

    def uninstall(self):
        t = self.getMapReduceObject()
        return t.uninstall()

    def get_reducer_hosts(self):
        t = self.getMapReduceObject()
        return t.get_reducer_hosts()



