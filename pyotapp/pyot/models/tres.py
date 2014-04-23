
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
from django.db.models.signals import pre_save, post_save
from pyot.models.rest import Resource
from django.core.validators import validate_slug
import py_compile
import pickle
import base64
from settings import TFMT

WAIT_TIMEOUT = 30

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

class EmulatorState(models.Model):
    timeAdded = models.DateTimeField(auto_now_add=True, blank=True) 
    _inp = models.CharField(max_length=1000, blank=True, null=True)
    _status = models.CharField(max_length=1000, blank=True, null=True)
    _out = models.CharField(max_length=1000, blank=True, null=True)
    _stack = models.CharField(max_length=1000, blank=True, null=True)
    result = models.TextField(db_column='result',default= '', max_length=4096)
    class Meta:
        app_label = 'pyot'  
    def set_input_data(self, data):
        self._inp = base64.encodestring(data)
    def get_input_data(self):
        return base64.decodestring(self._inp)
    inp = property(get_input_data, set_input_data)         
          

    def set_state_data(self, S):
        self._status = pickle.dumps(S)
    def get_state_data(self):
        return pickle.loads(self._status)
    status = property(get_state_data, set_state_data)     

    def getStatus(self):
        s = self.status
        return s

    def set_stack_data(self, S):
        self._stack = pickle.dumps(S)
    def get_stack_data(self):
        return pickle.loads(self._stack)
    stack = property(get_stack_data, set_stack_data) 

    def set_output_data(self, data):
        self._out = base64.encodestring(data)
    def get_output_data(self):
        return base64.decodestring(self._out)
    output = property(get_output_data, set_output_data) 

    def pop(self):
        t = self.stack
        p = t.pop()
        self.stack=t
        self.save()
        return p
    
    def push(self, d):
        print 'pushing', d
        t = self.stack
        t.append(d)
        self.stack=t
        self.save()

    def __unicode__(self):
        return u"{t}".format(t=self.timeAdded.strftime(TFMT))   

def init_stack(sender, instance, raw, **kwargs):
    if instance._stack is None:
        #print 'init stack'
        instance.stack = []
        instance.save()    
           
post_save.connect(init_stack, sender=EmulatorState)      
     
class TResT(models.Model):
    pf = models.ForeignKey(TResProcessing, related_name='ProcessingFunction')
    inputS = models.ManyToManyField(Resource)
    output = models.ForeignKey(Resource, related_name='OutputDestination', null=True)
    TResResource = models.ForeignKey(Resource, null=True, related_name='TresResource')
    state = models.CharField(max_length=10, blank=False, choices=TRES_STATES, default='CREATED')
    emu =  models.ForeignKey(EmulatorState, null=True)
    class Meta:
        app_label = 'pyot'
        
    def __unicode__(self):
        return u"Pf={p}, inputs={i}, output={o}".format(p=self.pf, i=str(self.inputS.all()), o=self.output)

    def deploy(self, TResResource):
        from pyot.tasks import deployTres

        #if TResResource.isinstance(Resource) == False:
        #    raise Exception('TResResource must be a Resource')
        if TResResource.uri != '/tasks':
            raise Exception('TResResource must have /tasks uri')
        self.TResResource=TResResource
        self.save()
        res = deployTres.apply_async(args=[self.id, TResResource.id], queue=TResResource.host.getQueue())
        res.wait()
        return res.result
        
         
    def uninstall(self): 
        from pyot.tasks import uninstallTres
        res = uninstallTres.apply_async(args=[self.id, self.TResResource.id], queue=self.TResResource.host.getQueue())
        res.wait()        
        self.state='CLEARED'
        self.save()
        return res.result
            
    def start(self):
        #TODO: do something only if task is not already started
        #send POST to TResResource
        if self.state == 'RUNNING':
            return 'Task is already running'        
        Pf = Resource.objects.get(host=self.TResResource.host, uri = '/tasks/'+self.pf.name)
        r = Pf.POST()
        print r.content, r.code
        if r.content == "Task now running":
            self.state='RUNNING' #TODO: change only if result is correct
            self.save()
        return r
         
    def stop(self):
        if self.state != 'RUNNING':
            return 'Task is not running'
        Pf = Resource.objects.get(host=self.TResResource.host, uri = '/tasks/'+self.pf.name)
        r = Pf.POST()  
        print r.content, r.code
        if r.content == "Task now halted":
            self.state='STOPPED'     #TODO: change only if result is correct
            self.save()
        return r    
        
    def getStatus(self):
        #TODO: 
        pass
    
    def getLastOutput(self):
        lo = Resource.objects.get(host=self.TResResource.host, uri = '/tasks/'+self.pf.name+'/lo')
        return lo
    
    def getInputSource(self):
        _is = Resource.objects.get(host=self.TResResource.host, uri = '/tasks/'+self.pf.name+'/is')
        return _is
    
    def getOutputDestination(self):
        _od = Resource.objects.get(host=self.TResResource.host, uri = '/tasks/'+self.pf.name+'/od')
        return _od    
    
    def emulate(self, duration=120):
        from rest import EventHandlerTres
        state = EmulatorState.objects.create()
        self.emu = state
        self.save()
        #create an event handler for this task
        h = EventHandlerTres.objects.create(task=self, description='Tres Handler: ', max_activations=1000)
        #for each input resource start an ObserveTask with the new handler 
        for inp in self.inputS.all():
            print 'Starting observe on ', inp
            inp.OBSERVE(duration=duration, handler=h.id)

    def runPf(self, inp):
        import sys
        self.emu.inp=inp
        self.emu.save()
        self.save()
        #from cStringIO import StringIO
        sys.path.append('/home/andrea/pyot/pyotapp/pyot/tres')
        sys.argv = [self.id]
        #oldio = (sys.stdin, sys.stdout, sys.stderr)
        #sio = StringIO()
        #sys.stdout = sys.stderr = sio   
        execfile(str(self.pf.sourcefile))
        print '\n'
        #sys.stdin, sys.stdout, sys.stderr = oldio 
        #print sio.getvalue()        
        #self.emu.result += sio.getvalue() 
        #self.emu.save()  
        
    def getEmuLastOutput(self):
        try:
            return self.emu.output
        except:
            return None
    def getEmuResult(self):
        return self.emu.result
