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
from __future__ import absolute_import
from celery import task
import celery
#from celery.task import task, periodic_task
from celery.signals import task_revoked
from pyot.models import *
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
import time, sys
from djcelery.models import TaskMeta
from django.conf import settings
import subprocess, os, signal
from pyot.rplApp import DAGupdate
import urllib
from netifaces import interfaces, ifaddresses, AF_INET6
import traceback

PROJECT_ROOT = settings.PROJECT_ROOT
tmpDir = settings.TRES_PWN_SCRIPT_TMP
CLEANUP_TASK_PERIOD = settings.CLEANUP_TASK_PERIOD
CLEANUP_TIME = settings.CLEANUP_TIME
SERVER_ADDRESS = settings.SERVER_ADDRESS
WORKER_RECOVERY = settings.WORKER_RECOVERY
RECOVERY_PERIOD = settings.RECOVERY_PERIOD
SUBSCRIPTION_RECOVERY = settings.SUBSCRIPTION_RECOVERY
RX_TIMEOUT = 20
COAP_PATH = PROJECT_ROOT + '/../libcoap-coap18/examples/'
COAP_CLIENT = COAP_PATH + 'coap-client'
RD_SERVER = COAP_PATH + 'rd'
DEFAULT_OBS_TIMEOUT = 30
TERM_CODE = '0.00'
saveMessageToDB = True
allowedMethods = ['get', 'post', 'put', 'delete']


def checkIp(ipAddress):
    """
    TODO
    """
    for ifaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET6, [{'addr':'No IP addr'}])]
        #print '%s: %s' % (ifaceName, ', '.join(addresses))
        #print ifaceName, addresses
        if ipAddress in addresses:
            return True
    return False

@task
def sendMailAdmin(subject, message):
    """
    TODO    
    """
    print 'sending mail to admins...'
    mail_admins(subject, message, fail_silently=False, connection=None, html_message=None)
    print '...Done'

def getFullUri(r):
    """
    TODO
    """
    return 'coap://[' + str(r.host.ip6address) + ']' + str(r.uri)

def coapRequest(method, uri, payload=None, timeout=None, observe=False, duration=60, inputfile=None, block=64):
    """
    TODO
    """
    if method not in allowedMethods:
        raise Exception('Method not allowed')
    if observe and method is not 'get':
        raise Exception('Observe works only with -get- method')

    print method + ' ' + uri

    req = COAP_CLIENT + ' -m ' + method
    if block:
        req = req + '  -b %s ' % str(block)

    if timeout:
        req = req + '  -B ' + str(timeout)
    if observe:
        req = req + ' -s ' + str(duration)
    if payload:
        req = req + ' -e ' + urllib.quote(payload, '')
    if inputfile:
        req = req + ' -f ' + inputfile

    req = req + ' ' + uri

    p = subprocess.Popen([req],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         shell=True)
    return p

class HostNotActive(Exception):
    """
    TODO
    """    
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def getResourceActive(rid):
    """
    TODO
    """    
    r = Resource.objects.get(id=rid)
    if r.host.active == False:
        raise HostNotActive(str(r.host.ip6address))
    uri = getFullUri(r)
    return r, uri

def getResource(rid):
    """
    TODO
    """    
    r = Resource.objects.get(id=rid)
    uri = getFullUri(r)
    return r, uri

def isTermCode(response):
    """
    TODO
    """    
    if response[0:4] == TERM_CODE:
        return True
    else:
        return False

def parseResponse(response):
    """
    TODO
    """    
    code = response[0:4]
    return code, response[5:]


#import datetime
def addQuery(uri, query):
    return uri + '?' + query

@task
def coapPost(ip6address, uri, payload, timeout=RX_TIMEOUT, query=None, inputfile=None, block=None, index=0):
    try:
        #st = (float(index) * 0.2)
        #time.sleep(st)
        #print st
        if query is not None:
            uri = addQuery(uri, query)
        fulluri = 'coap://[' + str(ip6address) + ']' + str(uri)
        p = coapRequest('post', fulluri, payload, timeout, inputfile, block=block)
        message = ''
        code = ''
        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                return Response(code, message)
            print 'response= ' + response
            code, m = parseResponse(response)
            message = message + m
            message = message.rstrip('\n')
    except ObjectDoesNotExist:
        return Response(FAILURE, 'Resource not found')
    except HostNotActive as e:
        return Response(FAILURE, 'Host ' + e.value + ' not active')
    except Exception as e:
        return Response(FAILURE, 'Exception Coap POST %s' % e)

@task
def coapGet(rid, payload, timeout=RX_TIMEOUT, query=None, block=None):
    try:
        r, uri = getResourceActive(rid)
        if query is not None:
            uri = addQuery(uri, query)
        p = coapRequest('get', uri, payload, timeout, block=block)
        code = ''
        message = ''
        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                if saveMessageToDB:
                    CoapMsg.objects.create(resource=r, method='GET', code=code, payload=message)
                return Response(code, message)
            print 'response= ' + response
            code, m = parseResponse(response)
            message = message + m
            message = message.rstrip('\n')

    except ObjectDoesNotExist:
        return Response(FAILURE, 'Resource not found')
    except HostNotActive as e:
        return Response(FAILURE, 'Host ' + e.value + ' not active')
    except Exception as e:
        return Response(FAILURE, 'Exception Coap GET %s' % e)

@task
def coapPut(rid, payload=None, timeout=RX_TIMEOUT, query=None, inputfile=None, block=None):
    try:
        _, uri = getResourceActive(rid)
        if query is not None:
            uri = addQuery(uri, query)
        p = coapRequest('put', uri, payload, timeout, inputfile=inputfile, block=block)
        message = ''
        code = ''
        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                return Response(code, message)
            print 'response= ' + response
            code, m = parseResponse(response)
            message = message + m
            message = message.rstrip('\n')
    except ObjectDoesNotExist:
        return Response(FAILURE, 'Resource not found')
    except HostNotActive as e:
        return Response(FAILURE, 'Host ' + e.value + ' not active')
    except Exception as e:
        return Response(FAILURE, 'Exception Coap PUT %s' % e)

@task
def coapDelete(rid, payload=None, timeout=RX_TIMEOUT, query=None):
    try:
        _, uri = getResourceActive(rid)
        if query is not None:
            uri = addQuery(uri, query)
        p = coapRequest('delete', uri, payload, timeout)
        message = ''
        code = ''
        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                return Response(code, message)
            print 'response= ' + response
            code, m = parseResponse(response)
            message = message + m
            message = message.rstrip('\n')
    except ObjectDoesNotExist:
        return Response(FAILURE, 'Resource not found')
    except HostNotActive as e:
        return Response(FAILURE, 'Host ' + e.value + ' not active')
    except Exception as e:
        return Response(FAILURE, 'Exception Coap DELETE %s' % e)

@task
def coapObserve(rid, payload=None, timeout=None, duration=DEFAULT_OBS_TIMEOUT, handler=None, renew=False):
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
            h = EventHandler.objects.get(id=int(handler))
            s = Subscription.objects.create(resource=r, duration=duration, pid=taskId, handler=h, renew=renew)
        else:
            s = Subscription.objects.create(resource=r, duration=duration, pid=taskId, renew=renew)

        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                break

            code, m = parseResponse(response)
            m = m.rstrip()
            if m.isdigit():
                print 'Observe update from ' + uri + ': ' + m
                m = CoapMsg.objects.create(resource=r, method='GET', code=code, payload=m, sub=s)

                if s.handler is not None:
                    print 'handling event!'
                    h = EventHandler.objects.filter(id=int(handler)).select_subclasses()
                    for i in h:
                        i.action(m)
        print 'subscription ended...'
        if renew:
            print 'renewing sub'
            coapObserve.apply_async(kwargs={'rid':rid, 'duration':duration, 'handler':handler, 'renew': renew}, queue=r.host.getQueue())
        else:
            s.active = False
            s.save()
    except ObjectDoesNotExist:
        return Response(FAILURE, 'Resource not found')
    except HostNotActive as e:
        return Response(FAILURE, 'Host ' + e.value + ' not active')

    except Exception, exc:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print ''.join('!! ' + line for line in lines)
        if s is not None:
            s.active = False
            s.save()
            print 'Subscription closed'
        coapObserve.retry(exc=exc, countdown=10)
    finally:
        if s is not None:
            s.active = False
            s.save()
            print 'Subscription closed'

@task_revoked.connect(sender=coapObserve)
def coapObserve_revoked_handler(sender, terminated, signum, args=None, task_id=None,
                      kwargs=None, **kwds):
    try:
        print 'Coap Observe revoked handler'
    except Exception as e:
        print e

def isObs(s):
    splitted = s.split(';')
    for i in splitted:
        if i.rstrip() == 'obs':
            return True
    return False


@task()
def coapDiscovery(host, path):
    print 'resource discovery: get well-Know on ip: ' + host
    Log.objects.create(log_type='discovery', message=host)

    uri = 'coap://[' + host + ']' + path
    print uri
    p = subprocess.Popen([COAP_CLIENT + ' -m get -b 64 ' + uri],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         shell=True)
    message = ''
    try:
        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                break
            print 'response= ' + response
            _, m = parseResponse(response)
            message = message + m
            message = message.rstrip('\n')
        splittedRes = message.split(',')
        h = Host.objects.get(ip6address=host)
        resList = []
        for link in splittedRes:
            parts = link.split(';')
            resUri = parts[0].strip('<>')
            resList.append(resUri)
            obs = isObs(link)
            title = None
            ct = None
            rt = None
            for part in parts:
                if part.startswith('title="'):
                    title = part[6:].strip('"')
                if part.startswith('rt="'):
                    rt = part[4:].strip('"')
                if part.startswith('ct='):
                    ct = part[3:]
            if resUri != '':
                try:
                    Resource.objects.get(uri=resUri, host=h)
                except ObjectDoesNotExist: #the resource is not registered, create a new record
                    #print 'Creating resource ' + resUri
                    Resource.objects.create(uri=resUri, host=h, obs=obs, title=title, ct=ct, rt=rt)
        return resList
    except ObjectDoesNotExist:
        return 'Host not found'
    except Exception as e:
        print 'Exception Coap Discovery: %s' % e


from pyot.resourceDirectory import createRdResources, CoAPServer
from twisted.internet import reactor

@task(max_retries=None)
def coapRdServer(prefix='bbbb::/64'):
    print 'starting Coap Resource Directory Server, prefix= ' + prefix
    #print 'id = ' + str(coapRdServer.request.id)
    n = Network.objects.get(network=prefix)
    """
    if coapRdServer.request.retries > 0:
        print 'coapRdServer retry #' + str(coapRdServer.request.retries)
        n.pid = str(coapRdServer.request.id)
        n.save()
        Log.objects.create(log_type='RdRetry', message=prefix)
    """    
    rdIp = prefix[:-3] + '1'
    if not checkIp(rdIp):
        raise Exception('Address %s not available' % rdIp)

    createRdResources(rdIp, n)
    try:    
        server = CoAPServer("[bbbb::1]", 5683)
        reactor.listenUDP(5683, server, "bbbb::1")
        coapRdServer.update_state(state="PROGRESS")
        reactor.run()   
    except Exception, exc:
        exc_type, exc_value, exc_traceback = sys.exc_info()              
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print ''.join('!! ' + line for line in lines)
        coapRdServer.update_state(state="ERROR")
        coapRdServer.retry(exc=exc, countdown=5)
    finally:
        n = Network.objects.get(network=prefix)
        n.pid = None
        n.save()
    """
    try:
        while True:
            time.sleep(5)
    except Exception, exc:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print ''.join('!! ' + line for line in lines)
        coapRdServer.update_state(state="ERROR")
        coapRdServer.retry(exc=exc, countdown=5)
    finally:
        n = Network.objects.get(network=prefix)
        n.pid = None
        n.save()
        #c.close()
    """

@celery.decorators.periodic_task(run_every=timedelta(seconds=CLEANUP_TASK_PERIOD))
def checkConnectedHosts():
    try:
        rlist = Host.objects.all()
        for i in rlist:
            if datetime.now() > timedelta(seconds=CLEANUP_TIME) + i.lastSeen and i.active == True:
                print 'cleaning host: ' + str(i.ip6address)
                i.active = False
                i.save()
                l = Log(log_type='clean', message=i)
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

    @celery.decorators.periodic_task(run_every=timedelta(seconds=RECOVERY_PERIOD))
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
            if network.pid is not None and network.pid != '':
                rdTaskObj = TaskMeta.objects.get(task_id=network.pid)
                print 'RD status = ' + rdTaskObj.status
                if rdTaskObj.status == 'FAILURE':
                    network.startRD()
                    Log.objects.create(log_type='RdRec', message=network.hostname)

            subSet = Subscription.objects.filter(active=True,
                                                 resource__host__network=network)
            for sub in subSet:
                try:
                    subTaskObj = TaskMeta.objects.get(task_id=sub.pid)
                    if subTaskObj.status == 'FAILURE':
                        print 'Failure sub: ', sub
                        #creates a new subscription
                        sub.resource.OBSERVE(duration=sub.duration,
                                             handler=sub.handler,
                                             renew=sub.renew)
                        Log.objects.create(log_type='SubRec', message=network.hostname)
                except TaskMeta.DoesNotExist:
                    pass


@task
def updateDAGs():
    ns = Network.objects.all()
    for n in ns:
        DAGupdate(n.id)


@task
def tresDownloadScript(filename):
    try:
        print 'downloading script'
        uri = 'http://' + SERVER_ADDRESS + '/media/scripts/' + filename
        print uri
        outFile = tmpDir + '/' + filename
        urllib.urlretrieve(uri, filename=outFile)
        return Response(SUCCESS, 'pyc downloaded')
    except Exception as e:
        return Response(FAILURE, str(e))
