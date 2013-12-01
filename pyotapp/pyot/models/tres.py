
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
from django.db.models.signals import pre_save
from pyot.models.rest import Resource

scriptFolder = 'scripts/'

class TResProcessing(models.Model):
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
    print 'Validating '  + str(instance.sourcefile) + ' ...'
    
    #check(instance.sourcefile)
    #raise Exception('nooo no no')
    
pre_save.connect(verifyPF, sender=TResProcessing)

class TResT(models.Model):
    pf = models.ForeignKey(TResProcessing, related_name='ProcessingFunction')
    inputS = models.ManyToManyField(Resource)
    output = models.ForeignKey(Resource, related_name='OutputDestination')
    class Meta:
        app_label = 'pyot'
    def __unicode__(self):
        return u"Pf={p}, inputs={i}, output={o}".format(p=self.pf, i=str(self.inputS.all()), o=self.output) 
    def deploy(self):
        pass
    def start(self):
        pass
    def stop(self):
        pass
    def getStatus(self):
        pass

