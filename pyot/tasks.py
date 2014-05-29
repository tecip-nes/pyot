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
from celery import Celery, task#, periodic_task
import celery
#from celery.task import task, periodic_task
from celery.signals import task_revoked
from pyot.models import *
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
import random, time, sys
from djcelery.models import TaskMeta
from pyot.settings import PROJECT_ROOT, CLEANUP_TASK_PERIOD, CLEANUP_TIME, SERVER_ADDRESS
from pyot.settings import WORKER_RECOVERY, RECOVERY_PERIOD, SUBSCRIPTION_RECOVERY, TRES_BASE
import subprocess, os, signal
from pyot.rplApp import DAGupdate
import urllib
from netifaces import interfaces, ifaddresses, AF_INET6
import random
import traceback

RX_TIMEOUT = 20
COAP_PATH = PROJECT_ROOT + '/../libcoap-4.0.1/examples/'
COAP_CLIENT = COAP_PATH + 'coap-client'
RD_SERVER = COAP_PATH + 'rd'
DEFAULT_OBS_TIMEOUT = 30
TERM_CODE = '0.00'
saveMessageToDB = True
allowedMethods = ['get','post','put','delete']


def checkIp(ipAddress):
    for ifaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET6, [{'addr':'No IP addr'}] )]
        #print '%s: %s' % (ifaceName, ', '.join(addresses))
        #print ifaceName, addresses
        if ipAddress in addresses:
            return True
    return False

@task
def sendMailAdmin(subject, message):
    print 'sending mail to admins...'
    mail_admins(subject, message, fail_silently=False, connection=None, html_message=None)
    print '...Done'

def getFullUri(r):
    return 'coap://[' + str(r.host.ip6address) + ']' + str(r.uri)

def coapRequest(method, uri, payload=None, timeout=None, observe=False, duration=60, inputfile=None, block=64):
    if method not in allowedMethods:
        raise Exception('Method not allowed')
    if observe and method is not 'get':
        raise Exception('Observe works only with -get- method')

    print method + ' ' + uri

    req = COAP_CLIENT + ' -m '+  method
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
    return code, response[5:]


#import datetime
def addQuery(uri, query):
    return uri + '?' + query

@task
def coapPost(ip6address, uri, payload, timeout = RX_TIMEOUT, query=None, inputfile=None, block=None, index=0):
    try:
        st = (float(index)*0.2)
        time.sleep(st)
        print st
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
        return 'Resource not found'
    except HostNotActive as e:
        return 'Host ' + e.value + ' not active'
    except Exception as e:
        print 'Exception Coap POST %s'  % e

@task
def coapGet(rid, payload, timeout = RX_TIMEOUT, query=None, block=None):
    try:
        r, uri = getResourceActive(rid)
        if query is not None:
            uri = addQuery(uri, query)
        p = coapRequest('get', uri, payload, timeout, block=block)
        code =''
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
        return 'Resource not found'
    except HostNotActive as e:
        return 'Host ' + e.value + ' not active'
    except Exception as e:
        print 'Exception Coap GET %s'  % e

@task
def coapPut(rid, payload=None, timeout = RX_TIMEOUT, query=None, inputfile=None, block=None):
    try:
        _r, uri = getResourceActive(rid)
        if query is not None:
            uri = addQuery(uri, query)
        p = coapRequest('put', uri, payload, timeout, inputfile=inputfile, block=block)
        message = ''
        code =''
        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                return Response(code, message)
            print 'response= ' + response
            code, m = parseResponse(response)
            message = message + m
            message = message.rstrip('\n')
    except ObjectDoesNotExist:
        return 'Resource not found'
    except HostNotActive as e:
        return 'Host ' + e.value + ' not active'
    except Exception, exc:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print ''.join('!! ' + line for line in lines)

@task
def coapDelete(rid, payload=None, timeout = RX_TIMEOUT, query=None):
    try:
        _r, uri = getResourceActive(rid)
        if query is not None:
            uri = addQuery(uri, query)
        p = coapRequest('delete', uri, payload, timeout)
        message = ''
        code =''
        while True:
            response = p.stdout.readline()
            if isTermCode(response):
                return Response(code, message)
            print 'response= ' + response
            code, m = parseResponse(response)
            message = message + m
            message = message.rstrip('\n')
    except ObjectDoesNotExist:
        return 'Resource not found'
    except HostNotActive as e:
        return 'Host ' + e.value + ' not active'
    except Exception, exc:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print ''.join('!! ' + line for line in lines)

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
                m = CoapMsg.objects.create(resource=r, method='GET', code=code, payload=m, sub = s)

                if s.handler is not None:
                    print 'handling event!'
                    h = EventHandler.objects.filter(id = int(handler)).select_subclasses()
                    for i in h:
                        i.action(m)
        print 'subscription ended...'
        if renew:
            print 'renewing sub'
            coapObserve.apply_async(kwargs={'rid':rid, 'duration':duration, 'handler':handler, 'renew': renew}, queue=r.host.getQueue())      
        else:
            s.active=False
            s.save()                             
    except ObjectDoesNotExist:
        return 'Resource not found'
    except HostNotActive as e:
        return 'Host ' + e.value + ' not active'

    except Exception, exc:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print ''.join('!! ' + line for line in lines)
        if s is not None:
            s.active=False
            s.save()
            print 'Subscription closed'
        coapObserve.retry(exc=exc, countdown=10)
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
    except Exception as e:
        print e

def isObs(s):
    splitted = s.split(';')
    for i in splitted:
        if i.rstrip() == 'obs':
            return True
    return False


@task()
def coapDiscovery(host, path=DEFAULT_DISCOVERY_PATH):
    print 'resource discovery: get well-Know on ip: ' + host
    Log.objects.create(log_type = 'discovery', message = host)

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
            _code, m = parseResponse(response)
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
                    Resource.objects.get(uri=resUri,host=h)
                except ObjectDoesNotExist:   #the resource is not registered, create a new record
                    #print 'Creating resource ' + resUri
                    Resource.objects.create(uri=resUri,host=h, obs = obs, title=title, ct=ct, rt=rt)
        return resList
    except ObjectDoesNotExist:
        return 'Host not found'
    except Exception as e:
        print 'Exception Coap Discovery: %s'  % e

@task(max_retries=None)
def coapRdServer(prefix = ''):
    print 'starting Coap Resource Directory Server, prefix= ' + prefix
    print 'id = ' + str(coapRdServer.request.id)
    if coapRdServer.request.retries > 0:
        print 'coapRdServer retry #' + str(coapRdServer.request.retries)
        n = Network.objects.get(network=prefix)
        n.pid=str(coapRdServer.request.id)
        n.save()
        Log.objects.create(log_type = 'RdRetry', message = prefix)
    rdIp = prefix[:-3] +'1'
    if not checkIp(rdIp):
        raise Exception('Address %s not available' % rdIp)
    try:
        coapRdServer.update_state(state="PROGRESS")
        rd = subprocess.Popen([RD_SERVER + ' -v 1 -A ' + rdIp],
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              shell=True)

        while True:
            response = rd.stdout.readline().strip()
            ipAddr= response.split(']')[0].split('[')[1]
            time = response.split()[1]
            print 'RD server, message from: ' + ipAddr + ' time = ' + time
            try:
                h = Host.objects.get(ip6address=ipAddr)
                h.lastSeen=datetime.now()
                h.active = True
                if int(time) < h.keepAliveCount:
                    Log.objects.create(log_type = 'registration', message = ipAddr)
                h.keepAliveCount = int(time)
                h.save()
                tmp = Resource.objects.filter(host=h)
                if len(tmp) == 0:
                    print 'The host has no resources.'
                    try:
                        h.DISCOVER()
                    except Exception:
                        pass
            except ObjectDoesNotExist: #the host does not exists, create a new Host
                h = Host(ip6address=ipAddr, lastSeen=datetime.now(), keepAliveCount = 1)
                h.save()
                try:
                    h.DISCOVER()
                except Exception:
                    pass
                Log.objects.create(log_type = 'registration', message = ipAddr)

    except Exception, exc:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print ''.join('!! ' + line for line in lines)
        coapRdServer.update_state(state="ERROR")
        coapRdServer.retry(exc=exc, countdown=5)
    finally:
        n = Network.objects.get(network=prefix)
        n.pid=None
        n.save()

        print 'finally, killing subprocesses...'
        if rd is not None:
            if os.path.exists("/proc/"+str(rd.pid)):
                os.kill(rd.pid, signal.SIGTERM)
        print '...done.'


@celery.decorators.periodic_task(run_every=timedelta(seconds=CLEANUP_TASK_PERIOD))
def checkConnectedHosts():
    try:
        rlist = Host.objects.all()
        for i in rlist:
            if datetime.now() > timedelta(seconds=CLEANUP_TIME) + i.lastSeen and i.active == True:
                print 'cleaning host: ' + str(i.ip6address)
                i.active=False
                i.save()
                l = Log(log_type = 'clean', message = i)
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
                    Log.objects.create(log_type = 'RdRec', message = network.hostname)

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
                        Log.objects.create(log_type = 'SubRec', message = network.hostname)
                except TaskMeta.DoesNotExist:
                    pass


@task
def updateDAGs():
    ns = Network.objects.all()
    for n in ns:
        DAGupdate(n.id)

tresCompile = TRES_BASE + 'apps/tres/tools/tres-pf-compile'
tresPMfeat = TRES_BASE + 'apps/tres/tres_pmfeatures.py'
tmpDir = '/tmp/'

@task
def deployTres(t_res_task_id, t_res_resource_id):

    totalTime = 0

    TResResource = Resource.objects.get(id=t_res_resource_id)
    TResTask = TResT.objects.get(id=t_res_task_id)

    #tresTaskUri = TResResource.getFullURI()+'/'+ TResTask.pf.name

    basename = os.path.basename(str(TResTask.pf.sourcefile))
    uri = 'http://' + SERVER_ADDRESS + '/media/scripts/' + basename
    outFile = tmpDir + basename

    urllib.urlretrieve(uri, filename=outFile)

    compile_command = tresCompile + ' ' + tresPMfeat + ' ' + outFile
    p = subprocess.check_call([compile_command],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True, cwd=tmpDir)

    start = datetime.now()
    end = datetime.now()
    diff = end-start

    fname = os.path.split(outFile)[1]

    try:
        newTask = Resource.objects.get(host=TResResource.host, uri = '/tasks/'+TResTask.pf.name)
    except Resource.DoesNotExist:
        newTask = Resource.objects.create(host=TResResource.host, uri = '/tasks/'+TResTask.pf.name)

    start = datetime.now()
    r = newTask.PUT()
    end = datetime.now()
    diff1 = end-start
    print 'first put result = '+ r.code
    if r.code != CREATED:
        newTask.delete()
        return 'Error creating new resource: ' + '/tasks/' + TResTask.pf.name

    start = datetime.now()
    TResResource.host.DISCOVER(TResResource.uri)
    TResResource.host.DISCOVER(TResResource.uri+'/'+ TResTask.pf.name)
    end = datetime.now()
    diff2 = end-start
    newIs = Resource.objects.get(host=TResResource.host, uri = '/tasks/'+TResTask.pf.name+'/is')
    newOd = Resource.objects.get(host=TResResource.host, uri = '/tasks/'+TResTask.pf.name+'/od')
    newPf = Resource.objects.get(host=TResResource.host, uri = '/tasks/'+TResTask.pf.name+'/pf')

    #print tmpDir + fname+'c'
    start = datetime.now()
    r =  newPf.PUT(inputfile=tmpDir + fname+'c', block=64)
    end = datetime.now()
    diff3 = end-start
    print 'PF put result = '+ r.code

    if r.code != CHANGED:
        return 'Error uploading processing function.'

    if TResTask.output:
        r = newOd.PUT(payload='<'+ TResTask.output.getFullURI() +'>')
        print 'OD put result = '+ r.code
        if r.code != CHANGED:
            return 'Error updating OD resource'
    for inp in TResTask.inputS.all():
        start = datetime.now()
        r = newIs.POST(payload='<'+ inp.getFullURI() +'>')
        print 'IS put result = '+ r.code
        end = datetime.now()
        diff4 = end-start
        if r.code != CHANGED:
            return 'Error updating OD resource'

    totalTime = str(diff1 + diff2 + diff3 + diff4)
    tot = totalTime+'\n'

    f = open('tres_local', 'a')
    f.write(tot)
    f.close()

    return 'Tres Task ' + str(TResTask) + ' Installed'

@task
def uninstallTres(t_res_task_id, t_res_resource_id):
    try:
        TResTask = TResT.objects.get(id=t_res_task_id)
        TResResource = Resource.objects.get(id=t_res_resource_id)
        newTask = Resource.objects.get(host=TResResource.host, uri = '/tasks/'+TResTask.pf.name)
        r = newTask.DELETE()
        if r.code == DELETED:
            newTask.delete()
            Resource.objects.filter(host=TResResource.host, uri__startswith='/tasks/'+TResTask.pf.name).delete()
            return 'Task ' + TResTask.pf.name+ ' uninstalled'
    except Exception, exc:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print ''.join('!! ' + line for line in lines)
        return 'Error uninstalling ' + TResTask.pf.name
