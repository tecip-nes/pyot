
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
import base64
import os
import pickle
import py_compile
import subprocess
import sys
import urllib

from django.conf import settings
from django.core.validators import validate_slug
from django.db import models
from django.db.models.signals import pre_save, post_save

from pyot.models.rest import *


MEDIA_ROOT = settings.MEDIA_ROOT
TFMT = settings.TFMT
SERVER_ADDRESS = settings.SERVER_ADDRESS
PROJECT_ROOT = settings.PROJECT_ROOT
tmpDir = settings.TRES_PWN_SCRIPT_TMP

WAIT_TIMEOUT = 30
T_RES_TOOLS = settings.PROJECT_PATH + '/../t-res-tools/'
SCRIPT_FOLDER = MEDIA_ROOT + 'scripts/'
tresCompile = T_RES_TOOLS + 'tres-pf-compile'
tresPMfeat = T_RES_TOOLS + 'tres_pmfeatures.py'


class TResProcessing(models.Model):
    """
    Defines a T-Res processing function. It is directly connected to a
    python source file. The source file is verified
    automatically each time the model is saved.
    """
    timeAdded = models.DateTimeField(auto_now_add=True, blank=True)
    name = models.CharField(max_length=10, validators=[validate_slug])
    description = models.CharField(max_length=500, blank=True, null=True)
    version = models.CharField(max_length=10, blank=True, null=True)
    sourcefile = models.FileField(upload_to=SCRIPT_FOLDER)

    class Meta(object):
        app_label = 'pyot'

    def get_file_size(self):
        return self.sourcefile.size

    def get_file_name(self):
        return self.sourcefile.name

    def __unicode__(self):
        return u"{n}".format(n=self.name)


def verify_pf(sender, instance, raw, **kwargs):
    '''
    Validates the syntax of the processing function
    '''
    print 'Validating ' + str(instance.sourcefile) + ' ...'
    py_compile.compile(str(instance.sourcefile), doraise=True)

pre_save.connect(verify_pf, sender=TResProcessing)

TRES_STATES = (
    (u'CREATED', u'CREATED'),
    (u'INSTALLED', u'INSTALLED'),
    (u'RUNNING', u'RUNNING'),
    (u'STOPPED', u'STOPPED'),
    (u'CLEARED', u'CLEARED'),
)


class EmulatorState(models.Model):
    """
    Defines the state of an emulator instance (input/output/stack...)
    """
    timeAdded = models.DateTimeField(auto_now_add=True, blank=True)
    _inp = models.CharField(max_length=1000, blank=True, null=True)
    _status = models.CharField(max_length=1000, blank=True, null=True)
    _out = models.CharField(max_length=1000, blank=True, null=True)
    _stack = models.CharField(max_length=1000, blank=True, null=True)
    result = models.TextField(db_column='result', default='', max_length=4096)

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
        self.stack = t
        self.save()
        return p

    def push(self, d):
        print 'pushing', d
        t = self.stack
        t.append(d)
        self.stack = t
        self.save()

    def __unicode__(self):
        return u"{t}".format(t=self.timeAdded.strftime(TFMT))


def init_stack(sender, instance, raw, **kwargs):
    if instance._stack is None:
        instance.stack = []
        instance.save()

post_save.connect(init_stack, sender=EmulatorState)


class TResT(models.Model):
    """
    Defines a model for a T-Res task. A Task is defined by its processing
    function, its input resources, and its output resources. A task
    may be instantiated on a TResResource, which is a common Resource object,
    or emulated on a PWN. In this case the state of the emulation is defined
    by the emu field.
    """
    pf = models.ForeignKey(TResProcessing, related_name='ProcessingFunction')
    inputS = models.ManyToManyField(Resource, blank=True, related_name='isource')
    output = models.ManyToManyField(Resource, blank=True, related_name='odestination')
    TResResource = models.ForeignKey(Resource, null=True,
                                     related_name='TresResource')
    state = models.CharField(max_length=10, blank=False, choices=TRES_STATES,
                             default='CREATED')
    period = models.IntegerField(default=0)
    emu = models.ForeignKey(EmulatorState, null=True)

    class Meta(object):
        app_label = 'pyot'

    def __unicode__(self):
        return u"Pf={p}, inputs={i}, output={o}".format(p=self.pf,
                                                        i=str(self.inputS.all()),
                                                        o=str(self.output.all()))

    def deploy(self, t_res_resource):
        """
        Installs the T-Res task on a T-Res resource. The installation is
        executed asynchronously by a PWN.
        """
        from pyot.tasks import tresDownloadScript

        if t_res_resource.uri != '/tasks':
            raise Exception('TResResource must have /tasks uri')
        self.TResResource = t_res_resource # FIXME only update if the installation is succesfull.

        # 1) compile the script
        basename = os.path.basename(str(self.pf.sourcefile))
        compile_command = tresCompile + ' ' + (tresPMfeat + ' '
                                               + str(self.pf.sourcefile))
        p = subprocess.check_call([compile_command],
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  shell=True, cwd=SCRIPT_FOLDER)
        # start a task downloading the script from the server
        pycFilename = basename + 'c'
        r = tresDownloadScript.apply_async(args=[pycFilename],
                                           queue=t_res_resource.host.getQueue())
        r.wait()
        result = r.result
        if result.code != SUCCESS:
            return Response(FAILURE, 'PWN: Error downloading pyc.')
        try:
            newTask = Resource.objects.get(host=self.TResResource.host,
                                           uri='/tasks/' + self.pf.name)
        except Resource.DoesNotExist:
            newTask = Resource.objects.create(host=self.TResResource.host,
                                              uri='/tasks/' + self.pf.name)

        # 3) Create a new task resource
        r = newTask.PUT(query="per=" + str(self.period))
        print 'first put result = ' + r.code
        if r.code != CREATED:
            newTask.delete()
            return Response(FAILURE, 'Error creating new resource: ' +
                            '/tasks/' + self.pf.name)

        newIs = Resource.objects.create(host=self.TResResource.host,
                                        uri='/tasks/' + self.pf.name + '/is')
        newOd = Resource.objects.create(host=self.TResResource.host,
                                        uri='/tasks/' + self.pf.name + '/od')
        newPf = Resource.objects.create(host=self.TResResource.host,
                                        uri='/tasks/' + self.pf.name + '/pf')
        _newLo = Resource.objects.create(host=self.TResResource.host,
                                         uri='/tasks/' + self.pf.name + '/lo')
        _newIn = Resource.objects.create(host=self.TResResource.host,
                                         uri='/tasks/' + self.pf.name + '/in')

        # 4) Upload the processing function
        r = newPf.PUT(inputfile=tmpDir + '/' + pycFilename, block=64)
        print 'PF put result = ' + r.code

        if r.code != CHANGED:
            self.uninstall()
            return Response(FAILURE, 'Error uploading processing function.')

        # 5) Create output destination resources
        for od in self.output.all():
            r = newOd.POST(payload='<' + od.getFullURI() + '>')
            print 'OD put result = ' + r.code + ' ' + od.getFullURI()
            if r.code != CHANGED:
                self.uninstall()
                return Response(FAILURE, 'Error updating OD resource')

        # 6) Create input source resources
        for inp in self.inputS.all():
            r = newIs.POST(payload='<' + inp.getFullURI() + '>')
            print 'IS put result = ' + r.code + ' ' + inp.getFullURI()
            if r.code != CHANGED:
                self.uninstall()
                return Response(FAILURE, 'Error updating IS resource')

        self.state = 'INSTALLED'
        self.save()  # update TResResource and state

        return Response(SUCCESS, 'Tres Task ' + str(self) + ' Installed')

    def uninstall(self):
        """
        Uninstalls a T-Res task from a node.
        """
        if self.state == 'RUNNING':
            self.stop()

        if self.state == 'CLEARED':
            return Response(SUCCESS, 'Task ' + self.pf.name +
                            'already uninstalled')

        newTask = Resource.objects.get(host=self.TResResource.host,
                                       uri='/tasks/' + self.pf.name)
        r = newTask.DELETE()
        if r.code == DELETED:
            newTask.delete()
            Resource.objects.filter(host=self.TResResource.host,
                                    uri__startswith='/tasks/' +
                                    self.pf.name).delete()
            self.state = 'CLEARED'
            self.save()
            return Response(SUCCESS, 'Task ' + self.pf.name + ' uninstalled')
        else:
            return Response(FAILURE, 'Error uninstalling task ' +
                            self.pf.name)

    def start(self):
        '''
        Activates a TRes Task by sending a POST request to the task resource.
        '''
        if self.state == 'RUNNING':
            return Response(SUCCESS, 'Task is already running')
        Pf = Resource.objects.get(host=self.TResResource.host,
                                  uri='/tasks/' + self.pf.name)
        r = Pf.POST(query="op=on")
        print str(self.TResResource), r.content, r.code
        if r.content == "Task now running":
            self.state = 'RUNNING'
            self.save()
        return r

    def stop(self):
        """
        Stops the execution of the T-Res Task.
        """
        if self.state != 'RUNNING':
            return Response(SUCCESS, 'Task is not running')
        Pf = Resource.objects.get(host=self.TResResource.host,
                                  uri='/tasks/' + self.pf.name)
        r = Pf.POST(query="op=off")
        print str(self.TResResource), r.content, r.code
        if r.content == "Task now halted":
            self.state = 'STOPPED'
            self.save()
        return r

    def get_status(self):
        """
        Not implemented yet.
        """
        raise NotImplementedError("Still to be implemented in T-Res")

    def getLastOutput(self):
        """
        Returns the last output resource reference. The resource can be
        retrieved or observed.
        """
        last_output = Resource.objects.get(host=self.TResResource.host,
                                           uri='/tasks/' +
                                           self.pf.name + '/lo')
        return last_output

    def getInputResource(self):
        """
        Returns the input resource reference. The resource can be
        retrieved or observed.
        """
        input_resource = Resource.objects.get(host=self.TResResource.host,
                                              uri='/tasks/' +
                                              self.pf.name + '/in')
        return input_resource

    def getInputSource(self):
        """
        Returns the list of Input Source resources.
        """
        _is = Resource.objects.get(host=self.TResResource.host,
                                   uri='/tasks/' + self.pf.name + '/is')
        return _is

    def getOutputDestination(self):
        """
        Returns the list of Output Destination resources.
        """
        _od = Resource.objects.get(host=self.TResResource.host,
                                   uri='/tasks/' + self.pf.name + '/od')
        return _od

    def emulate(self, duration=120):
        '''
        Manages the emulation of the T-Res task for a defined period of time.
        - create an event handler for this task
        - for each input resource start an ObserveTask with the new handler
        '''
        from pyot.models.rest import EventHandlerTres
        state = EmulatorState.objects.create()
        self.emu = state
        self.save()

        h = EventHandlerTres.objects.create(task=self,
                                            description='Tres Handler: ',
                                            max_activations=1000)

        for inp in self.inputS.all():
            print 'Starting observe on ', inp
            inp.OBSERVE(duration=duration, handler=h.id)

    def runPf(self, inp):
        """
        Runs the T-Res task on the PWN. This function is used in the emulation
        phase. First the source file is retrieved from the VCR and saved in
        /tmp dir. If the file has been already downloaded we use that copy.
        The parameter is the current input from an Input Source.
        """
        tmp_dir = '/tmp/'
        basename = os.path.basename(str(self.pf.sourcefile))
        outFile = tmp_dir + basename
        try:
            with open(outFile):
                pass
        except IOError:
            uri = 'http://' + SERVER_ADDRESS + '/media/scripts/' + basename
            urllib.urlretrieve(uri, filename=outFile)
        self.emu.inp = inp
        self.emu.save()
        self.save()
        #from cStringIO import StringIO
        sys.path.append(PROJECT_ROOT + '/tres')
        sys.argv = [self.id]
        #oldio = (sys.stdin, sys.stdout, sys.stderr)
        #sio = StringIO()
        #sys.stdout = sys.stderr = sio
        execfile(outFile)
        print '\n'
        #sys.stdin, sys.stdout, sys.stderr = oldio
        #print sio.getvalue()
        #self.emu.result += sio.getvalue()
        #self.emu.save()

    def getEmuLastOutput(self):
        """
        Returns the last output value of an emulation.
        """
        try:
            return self.emu.output
        except:
            return None

    def getEmuResult(self):
        """
        Returns the result of a processing function
        """
        return self.emu.result
