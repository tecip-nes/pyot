import common
from pyot.models import Resource
from datetime import datetime, timedelta
actuators = Resource.objects.filter(uri='/actuators/toggle', host__active=True)

start = datetime.now()

for a in actuators:
    print 'res: ' + str(a) + '  ' + a.POST()

stop =  datetime.now()   
elapsed = stop-start

print 'Toggled ' + str(len(actuators)) + ' actuators in ' + str(elapsed) + ' seconds'
