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


class TResPF(object):
    pf = None

    def __init__(self, fileRef, name, description=None, version=None):
        "default constructor, file-based"

        if type(fileRef) is not file:
            raise Exception('A file extension is required')
        # TODO: copy file in media folder
        self.pf = TResProcessing.objects.create(name=name,
                                                description=description,
                                                version=version,
                                                sourcefile=os.path.abspath(fileRef.name))

    @classmethod
    def fromSource(cls, sourceString, name, description=None, version=None):
        if name[-3:] != '.py':
            name += '.py'
        filename = name
        with open(SCRIPT_FOLDER + filename, 'w') as newFile:
            newFile.write(sourceString)
            newFile.flush()
            return cls(newFile, name[:-3], description, version)

    def getPfObject(self):
        return self.pf

    def __repr__(self):
        return self.pf.__unicode__()


class TResTask(object):
    taskId = None

    def __init__(self, TresPf, inputS=None, output=None, period=30):

        # First check if input resources are observable
        if inputS is not None:
            for inp in inputS:
                if inp.obs is False:
                    raise Exception('Input resources must be observable')
        # Then create task object
        task = TResT.objects.create(pf=TresPf.pf, period=period)
        self.taskId = task.id
        if inputS is not None:
            for inp in inputS:
                task.inputS.add(inp)

        if output is not None:
            if isinstance(output, Resource):
                task.output.add(output)
            else:
                for od in output:
                    task.output.add(od)
        task.save()

    def getTaskObject(self):
        return TResT.objects.get(id=self.taskId)

    def __repr__(self):
        t = self.getTaskObject()
        return t.__unicode__()

    def deploy(self, TResResource):
        t = self.getTaskObject()
        return t.deploy(TResResource)

    def uninstall(self):
        t = self.getTaskObject()
        return t.uninstall()

    def start(self):
        t = self.getTaskObject()
        return t.start()

    def stop(self):
        t = self.getTaskObject()
        return t.stop()

    def getStatus(self):
        t = self.getTaskObject()
        return t.getStatus()

    def getLastOutput(self):
        t = self.getTaskObject()
        return t.getLastOutput()

    def getInputResource(self):
        t = self.getTaskObject()
        return t.getInputResource()

    def getInputSource(self):
        t = self.getTaskObject()
        return t.getInputSource()

    def getOutputDestination(self):
        t = self.getTaskObject()
        return t.getOutputDestination()

    def emulate(self, duration=None):
        t = self.getTaskObject()
        return t.emulate(duration)

    def runPf(self, inp):
        t = self.getTaskObject()
        return t.runPf(inp)

    def getEmuLastOutput(self):
        t = self.getTaskObject()
        return t.getEmuLastOutput()

    def getEmuResult(self):
        t = self.getTaskObject()
        return t.getEmuResult()
