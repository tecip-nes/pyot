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

import common
from pyot.models import Resource, Host
from datetime import datetime, timedelta

checkResult = False

actuators = Resource.objects.filter(uri='/actuators/toggle', host__active=True)

start = datetime.now()

tasks = []

for a in actuators:
    tasks.append(a.asyncPOST())
    print 'starting Post on res: ' + str(a)

for task in tasks:
    #print 'wainting task PID:' + str(task)
    task.wait()
    print task.result
print 'Done'

stop =  datetime.now()   
elapsed = stop-start

print 'Toggled ' + str(len(actuators)) + ' actuators in ' + str(elapsed) + ' seconds'

print str(Host.objects.filter(active=True).count()) + '  hosts'
print str(Resource.objects.filter(host__active=True).count()) + '  resources'

if checkResult:
    print 'Checking Status...'

    tasks = []

    for a in actuators:
        tasks.append([a.asyncGET(), a])
        print 'starting Get on res: ' + str(a)

    for task in tasks:
        #print 'wainting task PID:' + str(task)
        task[0].wait()
        print str(task[1]) + ' status = ' +  task[0].result

    print 'Done'

