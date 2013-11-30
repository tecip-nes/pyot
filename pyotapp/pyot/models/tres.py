
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
from settings import MEDIA_ROOT
from django.core.files import File
import os
from django.db.models.signals import pre_save

scriptFolder = 'scripts/'

class TResPF(models.Model):
    timeAdded = models.DateTimeField(auto_now_add=True, blank=True) 
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=500, blank=True, null=True)
    version = models.CharField(max_length=10, blank=True, null=True)
    sourcefile = models.FileField(upload_to=scriptFolder)
    class Meta:
        app_label = 'pyot'
        
    def getFileSize(self):
        return self.sourcefile.size
    def getFileName(self):
        return self.sourcefile.name    
    def __unicode__(self):
        return u"{n}".format(n=self.name) 

def verifyPF(sender, instance, raw, **kwargs):
    print 'Validating '  + instance.sourcefile + ' ...'
    
    #check(instance.sourcefile)
    #raise Exception('nooo no no')
    
pre_save.connect(verifyPF, sender=TResPF)

class TResProcessingFunction(object):
    pf = None
    def __init__(self, fileRef, name, description=None, version=None):
        "default constructor, file-based"
        
        if type(fileRef) is not file:
            raise Exception('A file type is required')
        self.pf = TResPF.objects.create(name=name, 
                                         description=description,
                                         version=version,
                                         sourcefile=os.path.abspath(fileRef.name))
    
    @classmethod
    def fromSource(cls, sourceString, name, description=None, version=None):
        with open(MEDIA_ROOT + scriptFolder + name, 'w') as newFile:
            #newFile = open(MEDIA_ROOT + scriptFolder + name, 'w')
            newFile.write(sourceString)
            newFile.flush()
            return cls(newFile, name, description, version)
        
    def getPfObject(self):
        return self.pf
    
    def __repr__(self):
        return self.pf.__unicode__()
