'''
@author: Andrea Azzara' <a.azzara@sssup.it>
'''
from celery.task import task, periodic_task
from celery.signals import task_revoked
from models import *
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
import random, time


verbose = True

RX_TIMEOUT = 5

@task
def sendMailAdmin(subject, message):
    print 'sending mail to admins...'
    mail_admins(subject, message, fail_silently=False, connection=None, html_message=None)
    print '...Done'

#procs = []
from settings import PROJECT_ROOT
import subprocess
coapPath = PROJECT_ROOT + '/appsTesting/libcoap-4.0.1/examples/'
coapClient = coapPath + 'coap-client'
rdServer = coapPath + 'rd'
COAP_DEFAULT_TIMEOUT = 5
DEFAULT_OBS_TIMEOUT = 30
termCode = '0.00'
saveMessageToDB = True

def getFullUri(r):
    return 'coap://[' + r.host.ip6address + ']' + str(r.uri)


allowedMethods = ['get','post','put','delete']

def coapRequest(method, uri, payload=None, timeout=None, observe=False, duration=60):
    if method not in allowedMethods:
        raise Exception('Method not allowed')
    if observe and method is not 'get':
        raise Exception('Observe works only with -get- method')

    print method + ' ' + uri
    
    req = coapClient + ' -m '+  method

    if timeout:
        req = req + '  -B ' + str(timeout)
    if observe:
        req = req + ' -s ' + str(duration)
    if payload:
        req = req + ' e ' + payload

    req = req + ' ' + uri

    p = subprocess.Popen([req], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)    
    #procs.append(p) 
    return p

class HostNotActive(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def getResource(rid):
    r = Resource.objects.get(id=rid)
    if r.host.active == False:
        raise HostNotActive(r.host.ip6address)
    uri = getFullUri(r)
    return r, uri

def isTermCode(response):
    if response[0:4] == termCode:
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
    sl = (random.random()*600)/1000
    time.sleep(sl)
    print 'delay ', sl
    try:
        _r, uri = getResource(rid)
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
        r, uri = getResource(rid)
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
def coapObserve(rid, payload = None, timeout= None, duration = DEFAULT_OBS_TIMEOUT, handler=None):
    s = None
    try:
        r, uri = getResource(rid)
        p = coapRequest('get', uri, payload, observe=True, duration=duration)

        print 'OBSERVE PID = ' + coapObserve.request.id
        taskId = coapObserve.request.id #get task id

        if handler != None:
            h = EventHandler.objects.get(id = int(handler))
            s = Subscription.objects.create(resource=r, duration = duration, pid=taskId, handler=h)
        else:
            s = Subscription.objects.create(resource=r, duration = duration, pid=taskId )

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
    except ObjectDoesNotExist:
        return 'Resource not found'
    except HostNotActive as e:
        return 'Host ' + e.value + ' not active' 
    except Exception as e:
        print 'Exception Coap GET %s'  % e  
    finally:
        if s is not None:
            s.active=False
            s.save()
            print 'Subscription closed'

@task_revoked.connect(sender=coapObserve)
def coapObserve_revoked_handler(sender, terminated, signum, args=None, task_id=None,
                      kwargs=None, **kwds):
    try:
        print 'Coap Observe revoked handler'
        #rid = kwargs['rid']
    except Exception as e:
        print e


@task
def coapPut(rid, payload, timeout = RX_TIMEOUT):
    try:
        _r, uri = getResource(rid)
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

#(rate_limit='10/m')
@task(rate_limit='20/m')
def coapDiscovery(host):
    print 'resource discovery: get well-Know on ip: ' + host
    Log.objects.create(type = 'discovery', message = host)
    
    uri = 'coap://[' + host + ']/.well-known/core'
    print uri
    p = subprocess.Popen([coapClient + ' -m get ' + uri], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)    
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

@task
def coapRdServer():
    print 'starting Coap Resource Directory Server'
    try:
        coapRdServer.update_state(state="PROGRESS") #TODO ripristinare quando si usa mysql
        #logger = coapRdServer.get_logger()
        #logger.info("Starting task coapRdServer, pid = " + coapRdServer.request.id)
        p = subprocess.Popen([rdServer + ' -v 1 -A aaaa::1'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
 
        while True:
            response = p.stdout.readline().strip()
            ipAddr= response.split(']')[0].split('[')[1]
            print 'RD server, message from: ' + ipAddr 
            try:
                h = Host.objects.get(ip6address=ipAddr)
                h.lastSeen=datetime.now()
                if (h.active == False):
                    updateModTrace('Host')
                    coapDiscovery.delay(ipAddr)
                h.active = True
                h.keepAliveCount += 1
                h.save()
                tmp = Resource.objects.filter(host=h)
                if len(tmp) == 0:
                    print 'The host has no resources.'
                    coapDiscovery.delay(ipAddr)   
            except ObjectDoesNotExist:   #the does not exists, create a row in host-db
                h = Host(ip6address=ipAddr, lastSeen=datetime.now(), keepAliveCount = 1)
                h.save()  
                coapDiscovery.delay(ipAddr)
                updateModTrace('Host')
            #if rxr.message.payload == 'up':
            #    l = Log(type = 'registration', message = ipAddr)
            #    l.save()
    except Exception, exc:
        coapRdServer.update_state(state="ERROR")  #TODO ripristinare quando si usa mysql
        print 'Exception COAP SERVER %s' % exc
        p.kill()
        coapRdServer.retry(exc=exc, countdown=5)


@task_revoked.connect(sender=coapRdServer)
def my_task_revoked_handler(sender, terminated, signum, args=None,
                      kwargs=None, **kwds):
    print 'task revoked handler' + sender
    print terminated, signum
    #kill_child_processes(sender.worker_pid)

@periodic_task(run_every=timedelta(seconds=15))
def resourceIndexClean():
    
    try:
        rlist = Host.objects.all()
        for i in rlist:
            if datetime.now() > timedelta(seconds=20) + i.lastSeen and i.active == True:
                print 'cleaning host: ' + i.ip6address
                i.active=False
                i.save()
                updateModTrace('Host')
                l = Log(type = 'clean', message = i)
                l.save()
        return None        
    except Exception:
        pass    

@task
def pingTest(hostId, count=3):
    c = str(count)
    print 'starting Connectivity Test'
    cmdPre = 'ping6 '
    cmdPost = ' -I tun0 -c ' + c
    r = Host.objects.get(id=hostId)
    ipAddress = r.ip6address
    cmd = cmdPre + ipAddress + cmdPost
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout + stderr


