
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
from django.core.validators import validate_slug
import py_compile

scriptFolder = 'scripts/'

class TResProcessing(models.Model):
    timeAdded = models.DateTimeField(auto_now_add=True, blank=True) 
    name = models.CharField(max_length=10, validators=[validate_slug])
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
    py_compile.compile(str(instance.sourcefile), doraise=True)
    
pre_save.connect(verifyPF, sender=TResProcessing)

TRES_STATES = (
    (u'CREATED', u'CREATED'),
    (u'INSTALLED', u'INSTALLED'),    
    (u'RUNNING', u'RUNNING'),
    (u'STOPPED', u'STOPPED'),
    (u'CLEARED', u'CLEARED'),
)

class TResT(models.Model):
    pf = models.ForeignKey(TResProcessing, related_name='ProcessingFunction')
    inputS = models.ManyToManyField(Resource)
    output = models.ForeignKey(Resource, related_name='OutputDestination')
    TResResource = models.ForeignKey(Resource, null=True, related_name='TresResource', default='CREATED')
    state = models.CharField(max_length=10, blank=False, choices=TRES_STATES)
     
    class Meta:
        app_label = 'pyot'
        
    def __unicode__(self):
        return u"Pf={p}, inputs={i}, output={o}".format(p=self.pf, i=str(self.inputS.all()), o=self.output)
     
    def deploy(self, TResResource):
        if TResResource.isinstance(Resource) == False:
            raise Exception('TResResource must be a Resource')
        if TResResource.uri != '/tasks':
            raise Exception('TResResource must have /tasks uri')
        self.TResResource=TResResource
        #call code compiler
        #call tres client or call libcoap
        self.state=TRES_STATES['INSTALLED']
        self.save()         
         
    def uninstall(self): 
        #clear tres resource
        #self.TResResource.remove(TResResource)
        self.state=TRES_STATES['CLEARED']
        self.save()      
            
    def start(self):
        #send POST to TResResource
        self.TResResource.POST()
        self.state=TRES_STATES['RUNNING'] 
        self.save()   
         
    def stop(self):
        self.TResResource.POST()        
        self.state=TRES_STATES['STOPPED']     
        self.save()   
        
    def getStatus(self):
        pass
    
    def getLastOutput(self):
        loUri = '/tasks/%s/lo' % self.pf.name
        lo = Resource.objects.get(uri=loUri, host__ip6address=self.TResResource.host.ip6address)
        return lo
