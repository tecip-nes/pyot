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

