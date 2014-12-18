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
from datetime import datetime, timedelta
import logging

from django.conf import settings
from django.db import models
from model_utils.managers import InheritanceManager

from celery.task.control import revoke
from pyot.models.fields import IPNetworkField, IPNetworkQuerySet, IPAddressField
from pyot.tools.utils import get_celery_worker_status


TFMT = settings.TFMT
CACHING = True
DEFAULTCACHINGINTERVAL = 60
DEFAULT_CACHING_RESOURCES = {'/sensors/light': 15,
                             'temp': 120,
                             'baro': 180}

KEEPALIVEPERIOD = 10
WAIT_TIMEOUT = 10

COAP_REQ_TIMEOUT = 15

CACHING_RESOURCES = ['/sensors/light', 'temp', 'baro']

METHOD_CHOICES = (
    (u'GET', u'GET'),
    (u'PUT', u'PUT'),
    (u'POST', u'POST'),
    (u'DELETE', u'DELETE'),
)

# CoAP Method result code

CREATED = '2.01'
DELETED = '2.02'
VALID = '2.03'
CHANGED = '2.04'
CONTENT = '2.05'
NOT_ALLOWED = '4.04'
BAD_REQUEST = '4.00'
UNAUTHORIZED = '4.01'
BAD_OPTION = '4.02'
FORBIDDEN = '4.03'
NOT_FOUND = '4.04'
METHOD_NOT_ALLOWED = '4.05'
INTERNAL_SERVER_ERROR = '5.00'
NOT_IMPLEMENTED = '5.01'

SUCCESS = '1'
FAILURE = '0'

DEFAULT_DISCOVERY_PATH = '/.well-known/core'

CELERY_DEFAULT_QUEUE = 'celery'


def get_hosts_from_resources(resQeurySet):
    hsl = []
    for r in resQeurySet:
        hsl.append(r.host.id)
    return Host.objects.filter(id__in=hsl)


class Response(object):
    '''
    Defines response code and content typer for network operations
    '''
    code = None
    content = None

    def __init__(self, code="", content=""):
        self.code = code
        self.content = content

    def get_code(self):
        return self.code

    def get_content(self):
        return self.content

    def __unicode__(self):
        return u"%s - %s" % (self.code, self.content)

    def __str__(self):
        return u"%s - %s" % (self.code, self.content)


class Network(models.Model):
    '''
    Represents an IPv6 network. Each network can run a Resource directory
    server, defined by its pid (celery process identifier).
    '''
    objects = IPNetworkQuerySet.as_manager()
    network = IPNetworkField()
    hostname = models.CharField(max_length=30)
    pid = models.CharField(max_length=100, null=True, blank=True)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)

    def __unicode__(self):
        return u"%s - %s" % (self.network, self.hostname)

    def startRD(self):
        from pyot.tasks import coapRdServer
        rdServer = coapRdServer.apply_async(args=[str(self.network)],
                                            queue=self.hostname)
        """ possibly use this call to control all the parameters
        add.apply_async((2, 2), retry=True, retry_policy={
                'max_retries': 3,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            })
        """
        self.pid = rdServer.task_id
        self.save()
        return rdServer

    def stopRD(self):
        revoke(self.pid, terminate=True)
        self.pid = None
        self.save()

    def isConnected(self, table=None):
        if table is None:
            table = get_celery_worker_status()
        try:
            _e = table[self.hostname]
            return True
        except KeyError:
            return False

    def rplDagUpdate(self):
        from pyot.rplApp import DAGupdate
        return DAGupdate(self)

    class Meta(object):
        app_label = 'pyot'


class Host(models.Model):
    '''
    Defines an Ipv6 Host. Each host belongs to a network. Discovery and Ping
    operations can be started on a Host in order to discover available
    resources or test IP connectivity.
    '''
    ip6address = IPAddressField()
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)
    lastSeen = models.DateTimeField(blank=True)
    active = models.BooleanField(default=True)
    keepAliveCount = models.IntegerField(default=0)
    location = models.CharField(max_length=30, blank=True, default='')
    network = models.ForeignKey(Network, null=True, blank=True,
                                related_name='queue')

    def find_network(self):
        nets = Network.objects.all()
        for net in nets:
            if self.ip6address in net.network:
                return net
        return None

    def save(self, *args, **kwargs):
        network = self.find_network()
        if network:
            self.network = network
        super(Host, self).save(*args, **kwargs)

    def getQueue(self):
        if self.network:
            return self.network.hostname
        else:
            return CELERY_DEFAULT_QUEUE

    def __unicode__(self):
        return u"%s" % (self.ip6address)

    def PING(self, count=3):
        from pyot.tasks import pingHost
        res = pingHost.apply_async(args=[self.id, count],
                                   queue=self.getQueue())
        res.wait()
        return res.result

    def DISCOVER(self, path=DEFAULT_DISCOVERY_PATH):
        if self.active is False:
            return u'Host %s Not Active' % (str(self.ip6address))
        from pyot.tasks import coapDiscovery
        res = coapDiscovery.apply_async(args=[str(self.ip6address), path],
                                        queue=self.getQueue())
        # res.wait(timeout=COAP_REQ_TIMEOUT)
        return res

    class Meta(object):
        app_label = 'pyot'

class Resource(models.Model):
    '''
    Defines a CoAP Resource. Each resource belongs to a host. REST methods
    are available with both synchronous and asynchronous semantics.
    '''
    uri = models.CharField(max_length=39)
    host = models.ForeignKey(Host)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)
    extra = models.CharField(max_length=30, blank=True, default='')
    obs = models.BooleanField(default=False)
    rt = models.CharField(max_length=30, blank=True, null=True)
    title = models.CharField(max_length=30, blank=True, null=True)
    ct = models.CharField(max_length=3, blank=True, null=True)

    def __unicode__(self):
        return u"{ip} - {uri}".format(uri=self.uri, ip=self.host.ip6address)

    def getFullURI(self):
        return 'coap://[' + str(self.host.ip6address) + ']' + self.uri

    def getSubResources(self):
        subs = Resource.objects.filter(uri__startswith=self.uri + '/',
                                       host=self.host)
        return subs

    def GET(self, payload=None, timeout=5, query=None):
        if CACHING is True:
            value = getLastResponse(self)
            if value is not None:
                return value
        from pyot.tasks import coapGet
        res = coapGet.apply_async(args=[self.id, payload, timeout, query],
                                  queue=self.host.getQueue())
        res.wait()
        return res.result

    def PUT(self, payload=None, timeout=COAP_REQ_TIMEOUT, query=None,
            inputfile=None, block=None):
        from pyot.tasks import coapPut
        res = coapPut.apply_async(args=[self.id, payload, timeout,
                                        query, inputfile, block],
                                  queue=self.host.getQueue())
        res.wait()
        return res.result

    def POST(self, payload=None, timeout=COAP_REQ_TIMEOUT, query=None,
             inputfile=None, block=None, index=0):
        from pyot.tasks import coapPost
        res = coapPost.apply_async(args=[self.host.ip6address,
                                         self.uri,
                                         payload,
                                         timeout,
                                         query,
                                         inputfile,
                                         block,
                                         index],
                                   queue=self.host.getQueue())
        res.wait(timeout=15)
        return res.result

    def DELETE(self, payload=None, timeout=COAP_REQ_TIMEOUT, query=None):
        from pyot.tasks import coapDelete
        res = coapDelete.apply_async(args=[self.id,
                                           payload,
                                           timeout,
                                           query],
                                     queue=self.host.getQueue())
        res.wait()
        return res.result

    def asyncGET(self, payload=None, timeout=COAP_REQ_TIMEOUT, query=None):
        from pyot.tasks import coapGet
        res = coapGet.apply_async(args=[self.id,
                                        payload,
                                        timeout,
                                        query],
                                  queue=self.host.getQueue())
        return res

    def asyncPOST(self, payload=None, timeout=COAP_REQ_TIMEOUT, query=None,
                  inputfile=None, block=None, index=0):
        from pyot.tasks import coapPost
        res = coapPost.apply_async(args=[self.host.ip6address, self.uri,
                                         payload, timeout, query, inputfile,
                                         block, index],
                                   queue=self.host.getQueue())
        return res

    def asyncPUT(self, payload=None, timeout=COAP_REQ_TIMEOUT, query=None,
                 inputfile=None, block=None):
        from pyot.tasks import coapPut
        res = coapPut.apply_async(args=[self.id, payload, timeout, query,
                                        inputfile, block],
                                  queue=self.host.getQueue())
        return res

    def OBSERVE(self, duration, handler, renew=False):
        from pyot.tasks import coapObserve
        res = coapObserve.apply_async(kwargs={'rid': self.id,
                                              'duration': duration,
                                              'handler': handler,
                                              'renew': renew},
                                      queue=self.host.getQueue())
        return res

    class Meta(object):
        app_label = 'pyot'


class EventHandler(models.Model):
    '''
    Abstract class defining the basic structure of an event handler.
    InheritanceManager is used to create the subclasses.
    '''
    description = models.CharField(max_length=100)
    activationCount = models.IntegerField(default=0)
    max_activations = models.IntegerField(null=True, blank=True)
    objects = InheritanceManager()
    result = models.CharField(max_length=100, null=True, blank=True)
    timeString = models.FloatField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def action(self, res):
        raise NotImplementedError("Subclasses are responsible for creating this method")

    def __unicode__(self):
        return u"{description} | Activations = {activationCount} | Max = {max_activations} - active={active}".format(description=self.description,
                                                                                             activationCount=self.activationCount,
                                                                                                max_activations=self.max_activations,
                                                                                                active=self.active)

    class Meta(object):
        app_label = 'pyot'


class Subscription(models.Model):
    '''
    Model representing a subscription. Each subscription corresponds to a
    task (identified by a celery pid). Subscriptions may be automatically
    renewed.
    '''
    resource = models.ForeignKey(Resource)
    duration = models.IntegerField(default=15)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)
    pid = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    handler = models.ForeignKey(EventHandler, null=True, blank=True)
    renew = models.BooleanField(default=False)

    def __unicode__(self):
        return u"{t} {uri} - duration={duration} - active={active} - renew={r}".format(uri=self.resource,
                                                          duration=self.duration,
                                                          t=self.timeadded.strftime(TFMT),
                                                          r=self.renew,
                                                          active=self.active)

    def cancel_subscription(self):
        revoke(self.pid, terminate=True)
        self.active = False
        self.save()

    class Meta(object):
        app_label = 'pyot'


class CoapMsg(models.Model):
    '''
    Model representing a CoAP Message. It may be associated with a
    subscription. The payload is encoded in base64.
    '''
    resource = models.ForeignKey(Resource)
    method = models.CharField(max_length=10, blank=False, choices=METHOD_CHOICES)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)
    code = models.CharField(max_length=5, null=True, blank=True)
    sub = models.ForeignKey(Subscription, null=True, blank=True)
    _payload = models.TextField(db_column='payload', blank=True, max_length=1024)

    def set_data(self, data):
        self._payload = base64.encodestring(data)

    def get_data(self):
        return base64.decodestring(self._payload)

    payload = property(get_data, set_data)

    def __unicode__(self):
        return u"{t} {method} {uri}: {payload}".format(uri=self.resource.uri,
                                                       method=self.method,
                                                       payload=self.payload,
                                                       t=self.timeadded.strftime(TFMT))

    class Meta(object):
        app_label = 'pyot'


def getLastResponse(resource):
    '''
    Caching mechanism: tries to find a recent value received from the resource.
    '''
    if resource.uri not in CACHING_RESOURCES:
        return None
    try:
        interval = DEFAULT_CACHING_RESOURCES[resource.uri]
    except:
        interval = DEFAULTCACHINGINTERVAL
    now = datetime.now()
    i = timedelta(seconds=interval)
    start = now - i
    msgs = CoapMsg.objects.filter(resource__id=resource.id,
                                  timeadded__gte=start).exclude(method='PUT').order_by('-id')
    if msgs.count() == 0:
        return None
    return Response(code=msgs[0].code, content=msgs[0].payload)


class EventHandlerMsg(EventHandler):
    '''
    Event handler sending a message to a CoAP resource.
    '''
    msg = models.ForeignKey(CoapMsg)

    def __unicode__(self):
        return u"{meta}".format(meta=self.description)

    def action(self, msg=None):
        logging.debug('ACTION')
        from pyot.Events import sendMsg
        if self.activationCount == self.max_activations:
            logging.debug('max activations reached')
            return
        self.activationCount += 1
        self.result = sendMsg(self.msg)
        self.save()

    class Meta(object):
        app_label = 'pyot'


class EventHandlerTres(EventHandler):
    '''
    Event handler activating a TRes task (emulation mode).
    '''
    from tres import TResT

    task = models.ForeignKey(TResT)

    def __unicode__(self):
        return u"{meta}".format(meta=self.description)

    def action(self, msg):
        print 'ACTION, activating tres'
        if self.activationCount == self.max_activations:
            logging.debug('max activations reached')
            return
        self.task.runPf(msg.payload)
        self.activationCount += 1
        self.save()

    class Meta(object):
        app_label = 'pyot'
