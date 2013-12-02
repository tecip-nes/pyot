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

from pyot.models.tres import *
from settings import MEDIA_ROOT
import os

class TResPF(object):
    pf = None
    def __init__(self, fileRef, name, description=None, version=None):
        "default constructor, file-based"
        
        if type(fileRef) is not file:
            raise Exception('A file type is required')
        self.pf = TResProcessing.objects.create(name=name, 
                                         description=description,
                                         version=version,
                                         sourcefile=os.path.abspath(fileRef.name))
    
    @classmethod
    def fromSource(cls, sourceString, name, description=None, version=None):
        with open(MEDIA_ROOT + scriptFolder + name, 'w') as newFile:
            newFile.write(sourceString)
            newFile.flush()
            return cls(newFile, name, description, version)
        
    def getPfObject(self):
        return self.pf
    
    def __repr__(self):
        return self.pf.__unicode__()

class TResTask(object):
    task = None
    def __init__(self, pf, inputS, output):
        #First check if input resources are observable
        for inp in inputS:
            if inp.obs==False:
                raise Exception('Input resources must be observable')          
        #Then create task object
        self.task = TResT.objects.create(pf = pf, output = output)
        for inp in inputS:
            self.task.inputS.add(inp)
        self.task.save()    

    def getTaskObject(self):
        return self.task    

    def __repr__(self):
        return self.task.__unicode__()
    def deploy(self,TResResource):
        return self.task.deploy(TResResource)
    def uninstall(self):   
        return self.task.uninstall()
    def start(self):
        return self.task.start()
    def stop(self):
        return self.task.stop()
    def getStatus(self):
        return self.task.getStatus()
    def getLastOutput(self):
        return self.task.getLastOutput()
