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
from celery.task import task, periodic_task
from celery.signals import task_revoked
from models import *
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
import random, time, sys
from djcelery.models import TaskMeta
from settings import PROJECT_ROOT, CLEANUP_TASK_PERIOD, CLEANUP_TIME
from settings import WORKER_RECOVERY, RECOVERY_PERIOD, SUBSCRIPTION_RECOVERY
import subprocess, os, signal

RX_TIMEOUT = 5
COAP_PATH = PROJECT_ROOT + '/appsTesting/libcoap-4.0.1/examples/'
COAP_CLIENT = COAP_PATH + 'coap-client'
RD_SERVER = COAP_PATH + 'rd'
COAP_DEFAULT_TIMEOUT = 5
DEFAULT_OBS_TIMEOUT = 30
TERM_CODE = '0.00'
saveMessageToDB = True
allowedMethods = ['get','post','put','delete']

@task
def sendMailAdmin(subject, message):
    print 'sending mail to admins...'
    mail_admins(subject, message, fail_silently=False, connection=None, html_message=None)
    print '...Done'

def getFullUri(r):
    return 'coap://[' + str(r.host.ip6address) + ']' + str(r.uri)

def coapRequest(method, uri, payload=None, timeout=None, observe=False, duration=60):
    if method not in allowedMethods:
        raise Exception('Method not allowed')
    if observe and method is not 'get':
        raise Exception('Observe works only with -get- method')

    print method + ' ' + uri
    
    req = COAP_CLIENT + ' -m '+  method

    if timeout:
        req = req + '  -B ' + str(timeout)
    if observe:
        req = req + ' -s ' + str(duration)
    if payload:
        req = req + ' e ' + payload

    req = req + ' ' + uri

    p = subprocess.Popen([req], 
                         stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE, 
                         shell=True)    
    return p

class HostNotActive(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def getResourceActive(rid):
    r = Resource.objects.get(id=rid)
    if r.host.active == False:
        raise HostNotActive(str(r.host.ip6address))
    uri = getFullUri(r)
    return r, uri

def getResource(rid):
    r = Resource.objects.get(id=rid)
    uri = getFullUri(r)
    return r, uri

def isTermCode(response):
    if response[0:4] == TERM_CODE:
        return True
    else:
        return False

def parseResponse(response):
    code = response[0:4]  
    if code != '2.05':
        return code, ''
    else:
        return code, response[5:]


def retMes(code, message):
    if code != '2.05':
        return code
    elif (message == None or message == '' or message=='\n'):
        return code
    else:
        return message


@task
def coapPost(rid, payload, timeout = RX_TIMEOUT):
    try:
        _r, uri = getResourceActive(rid)
        p = coapRequest('post', uri, payload, timeout)
        message = '' 
        code = '0.00'
        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                #CoapMsg.objects.create(resource=r, method='POST', code=code, payload=message) 
                return retMes(code, message)
            print 'response= ' + response 
            code, m = parseResponse(response)
            message = message + m
            message = message.rstrip('\n')
    except ObjectDoesNotExist:
        return 'Resource not found'
    except HostNotActive as e:
        return 'Host ' + e.value + ' not active' 
    except Exception as e:
        print 'Exception Coap POST %s'  % e        

@task
def coapGet(rid, payload, timeout = RX_TIMEOUT):
    try:
        r, uri = getResourceActive(rid)
        p = coapRequest('get', uri, payload, timeout)
        code =''
        message = '' 
        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                if saveMessageToDB:
                    CoapMsg.objects.create(resource=r, method='GET', code=code, payload=message) 
                return retMes(code, message)
            print 'response= ' + response 
            code, m = parseResponse(response)
            message = message + m
            message = message.rstrip('\n')
        
    except ObjectDoesNotExist:
        return 'Resource not found'
    except HostNotActive as e:
        return 'Host ' + e.value + ' not active' 
    except Exception as e:
        print 'Exception Coap GET %s'  % e


@task
def coapObserve(rid, payload = None, timeout= None, duration = DEFAULT_OBS_TIMEOUT, handler=None, renew=False):
    if coapObserve.request.retries > 1:
        print 'coapObserve retry #' + str(coapObserve.request.retries) + '  rid=' + str(rid)    
    
    s = None
    try:
        r, uri = getResourceActive(rid)
        p = coapRequest('get', uri, payload, observe=True, duration=duration)
        coapObserve.update_state(state="PROGRESS")
        print 'OBSERVE PID = ' + coapObserve.request.id
        taskId = coapObserve.request.id #get task id

        if handler != None:
            h = EventHandler.objects.get(id = int(handler))
            s = Subscription.objects.create(resource=r, duration = duration, pid=taskId, handler=h, renew=renew)
        else:
            s = Subscription.objects.create(resource=r, duration = duration, pid=taskId, renew=renew)

        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                break 
            
            code, m = parseResponse(response)
            m = m.rstrip() 
            if m.isdigit(): 
                print 'Observe update from ' + uri + ': ' + m
                CoapMsg.objects.create(resource=r, method='GET', code=code, payload=m, sub = s) 

                if s.handler is not None:
                    print 'handling event!'
                    h = EventHandler.objects.filter(id = int(handler)).select_subclasses()
                    for i in h:
                        i.action() 
        print 'subscription ended...'                
        if renew:
            print 'renewing sub'
            coapObserve.apply_async(kwargs={'rid':rid, 'duration':duration, 'handler':handler, 'renew': renew}, queue=r.host.getQueue())                               
    except ObjectDoesNotExist:
        return 'Resource not found'
    except HostNotActive as e:
        return 'Host ' + e.value + ' not active' 
    except Exception, exc:
        print 'Exception COAP SERVER %s' % exc
        if s is not None:
            s.active=False
            s.save()
            print 'Subscription closed'        
        coapObserve.retry(exc=exc, countdown=10)        
    finally:
        if s is not None and SUBSCRIPTION_RECOVERY == False:
            s.active=False
            s.save()
            print 'Subscription closed'

@task_revoked.connect(sender=coapObserve)
def coapObserve_revoked_handler(sender, terminated, signum, args=None, task_id=None,
                      kwargs=None, **kwds):
    try:
        print 'Coap Observe revoked handler'
    except Exception as e:
        print e


@task
def coapPut(rid, payload, timeout = RX_TIMEOUT):
    try:
        _r, uri = getResourceActive(rid)
        p = coapRequest('put', uri, payload, timeout)
        message = '' 
        code =''
        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                return retMes(code, message)
            print 'response= ' + response 
            code, m = parseResponse(response)
            message = message + m
            message = message.rstrip('\n')
    except ObjectDoesNotExist:
        return 'Resource not found'
    except HostNotActive as e:
        return 'Host ' + e.value + ' not active' 
    except Exception as e:
        print 'Exception Coap GET %s'  % e

def isObs(s):
    splitted = s.split(';')
    for i in splitted:
        if i.rstrip() == 'obs':
            return True
    return False

@task()
def coapDiscovery(host):
    print 'resource discovery: get well-Know on ip: ' + host
    Log.objects.create(type = 'discovery', message = host)
    
    uri = 'coap://[' + host + ']/.well-known/core'
    print uri
    p = subprocess.Popen([COAP_CLIENT + ' -m get ' + uri], 
                         stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE, 
                         shell=True)    
    message = '' 
    while True:
        response = p.stdout.readline()
        if isTermCode(response):
            break
        print 'response= ' + response 
        _code, m = parseResponse(response)
        message = message + m
        message = message.rstrip('\n')
    splittedRes = message.split(',')
    try:
        h = Host.objects.get(ip6address=host)
        resList = []
        for link in splittedRes:
            resUri = link.split(';')[0].strip('<>')
            resList.append(resUri)
            obs = isObs(link)
            if resUri != '':
                try:
                    Resource.objects.get(uri=resUri,host=h)
                except ObjectDoesNotExist:   #the resource is not registered, create a new record
                    print 'Creating resource ' + resUri
                    Resource.objects.create(uri=resUri,host=h, obs = obs)
        return resList    
    except ObjectDoesNotExist:
        return 'Host not found'
    except Exception as e:
        print 'Exception Coap Discovery: %s'  % e

def updateModTrace(sender):
    try:
        m = ModificationTrace.objects.get(className=sender)
        m.lastModified=datetime.now()
        m.save()
    except ObjectDoesNotExist:
        ModificationTrace.objects.create(className=sender)  

import traceback

@task
def coapRdServer(prefix = ''):
    print 'starting Coap Resource Directory Server'
    try:
        coapRdServer.update_state(state="PROGRESS") 
        rd = subprocess.Popen([RD_SERVER + ' -v 1 -A aaaa::1'], 
                              stdin=subprocess.PIPE, 
                              stdout=subprocess.PIPE, 
                              shell=True)
 
        while True:
            response = rd.stdout.readline().strip()
            ipAddr= response.split(']')[0].split('[')[1]
            print 'RD server, message from: ' + ipAddr 
            try:
                h = Host.objects.get(ip6address=ipAddr)
                h.lastSeen=datetime.now()
                if (h.active == False):
                    updateModTrace('Host')
                    h.DISCOVER()
                h.active = True
                h.keepAliveCount += 1
                h.save()
                tmp = Resource.objects.filter(host=h)
                if len(tmp) == 0:
                    print 'The host has no resources.'
                    h.DISCOVER()   
            except ObjectDoesNotExist: #the host does not exists, create a new Host
                h = Host(ip6address=ipAddr, lastSeen=datetime.now(), keepAliveCount = 1)
                h.save()  
                h.DISCOVER()
                updateModTrace('Host')
            #if rxr.message.payload == 'up':
            #    l = Log(type = 'registration', message = ipAddr)
            #    l.save()
    except Exception, exc:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print ''.join('!! ' + line for line in lines)  
        coapRdServer.update_state(state="ERROR")  
        coapRdServer.retry(exc=exc, countdown=5)
    finally:
        print 'finally, killing subprocesses...'
        if rd is not None:    
            os.killpg(rd.pid, signal.SIGTERM)
        print '...done.'


@periodic_task(run_every=timedelta(seconds=CLEANUP_TASK_PERIOD))
def checkConnectedHosts():
    try:
        rlist = Host.objects.all()
        for i in rlist:
            if datetime.now() > timedelta(seconds=CLEANUP_TIME) + i.lastSeen and i.active == True:
                print 'cleaning host: ' + str(i.ip6address)
                i.active=False
                i.save()
                updateModTrace('Host')
                l = Log(type = 'clean', message = i)
                l.save()
        return None        
    except Exception:
        pass    

@task
def pingHost(hostId, count=3):
    c = str(count)
    print 'starting Connectivity Test'
    cmdPre = 'ping6 '
    cmdPost = ' -I tun0 -c ' + c
    r = Host.objects.get(id=hostId)
    ipAddress = str(r.ip6address)
    cmd = cmdPre + ipAddress + cmdPost
    p = subprocess.Popen(cmd, 
                         shell=True, 
                         stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout + stderr

if WORKER_RECOVERY:
    @periodic_task(run_every=timedelta(seconds=RECOVERY_PERIOD))
    def recoveryWorkers():
        """
        Recoveries lost workers status:
        Useful in case a worker node resets. When the node connects again
        the function tries to restart a lost RD server and possible active
        subscriptions. 
        """
        networks = Network.objects.all()
        #TaskMeta.objects.filter(status=states.SUCCESS).delete()
        for network in networks:
            if network.isConnected() == False:
                continue
            print network.hostname
            if network.pid is not None:
                rdTaskObj = TaskMeta.objects.get(task_id=network.pid)
                print 'RD status = ' + rdTaskObj.status
                if rdTaskObj.status == 'FAILURE':
                    network.startRD()
                    
            subSet = Subscription.objects.filter(active=True,
                                                 resource__host__kqueue=network)
            for sub in subSet:
                try:
                    subTaskObj = TaskMeta.objects.get(task_id=sub.pid)
                    if subTaskObj.status == 'FAILURE':
                        print 'Failure sub: ', sub
                        #creates a new subscription
                        sub.resource.OBSERVE(duration=sub.duration,
                                             handler=sub.handler,
                                             renew=sub.renew)
                except TaskMeta.DoesNotExist:
                    pass

