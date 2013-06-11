'''
@author: Andrea Azzara' <a.azzara@sssup.it>
'''
from models import *
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist

def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    return d


def get_statistics():
    hosts = Host.objects.filter()
    hostsactiveCount = Host.objects.filter(active=True).count()
    Resources = Resource.objects.filter(host__active=True).exclude(uri ='.well-known')

    hostcount = hosts.count()
    
    rescount = Resources.count()

    #server started
    now = datetime.now()
    try:
        server = RunningServer.objects.get()

        startT = server.timeadded
        starttime = startT.strftime(tfmt)
        #server uptime
        uptime = now - startT   
        messub = CoapMsg.objects.exclude(sub=None).filter(timeadded__gte=startT)
        messubcount = messub.count()

        disc = Log.objects.filter(type = 'discovery', timeadded__gte=startT)
        discs = disc.count()
        canc = Log.objects.filter(type = 'clean', timeadded__gte=startT)
        cleancount = canc.count()
        reg = Log.objects.filter(type = 'registration', timeadded__gte=startT)
        regcount = reg.count()

        timealive = now - startT
        timealiveSecs = (timealive.microseconds + (timealive.seconds + timealive.days * 24 * 3600) * 10**6) / 10**6

        perHost = []
        for h in hosts:
            ip = h.ip6address
            disc = Log.objects.filter(type = 'discovery', message = ip, timeadded__gte=startT)
            discount = disc.count()
            canc = Log.objects.filter(type = 'clean', message = ip, timeadded__gte=startT)
            cleancount = canc.count()
            reg = Log.objects.filter(type = 'registration', message = ip, timeadded__gte=startT)
            regcount = reg.count()
            active = h.active
            lastSeen = h.lastSeen
            keepaliveCount = h.keepAliveCount

           
            if h.active == True:
                expectedMessages = timealiveSecs / KEEPALIVEPERIOD
                p = float(keepaliveCount)*100 / float(expectedMessages)
                perc =  "%.2f" % p
            else:
                expectedMessages = 'None'
                perc = 'None'   

           


            dic = {'ip': ip,
                  'discount': discount,
                  'cleancount':cleancount,
                  'regcount':regcount,
                  'active':active,
                  'lastSeen':lastSeen.strftime(tfmt),
                  'kacount': keepaliveCount,
                  'expected': expectedMessages,
                  'perc': perc}
            perHost.append(dic)  
        ''' 
        perSub = []
        subs = Subscription.objects.filter(active=True)
        for s in subs:
           messcount = CoapMsg.objects.filter(sub = s).count()
           dic = {'res': s.resource,
                  'type': s.subtype,
                  'period': s.period,
                  'thr': s.threshold,
                  'timeadded':s.timeadded.strftime(tfmt),
                  'messcount': messcount} 
           perSub.append(dic)         
        '''
        #per resource /subscription count / expected 
        #excludeList = ['.well-known', 'mnt']
        #Resources = Resource.objects.filter(host__active=True).exclude(uri__in=excludeList)   

        d = {'starttime':starttime, 
                    'uptime': uptime,
                    'timealiveSecs': timealiveSecs,
                    'rescount': rescount, 
                    'hostcount':hostcount, 
                    'hostsactiveCount': hostsactiveCount,
                    'msgsubs': messubcount,
                    'discoveries':discs,
                    'registrations' :regcount,
                    'canceled': cleancount,
                    'perHost':perHost}
                    #'perSub':perSub}


        return d
    except ObjectDoesNotExist:
        return {}
