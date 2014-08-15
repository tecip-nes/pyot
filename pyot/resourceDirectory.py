'''
Created on Aug 6, 2014

@author: andrea
'''

from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist

from pyot.models import Resource, Host, Log
"""
import sys
PY_COAP_PATH = '../'

sys.path.insert(0, PY_COAP_PATH)
"""
from coapthon2.server.coap_protocol import CoAP
from coapthon2.resources.resource import Resource as pResource
#from example_resources import Storage, Separate

def createRdResources(rdIp, n):
    try:
        rdHost = Host.objects.get(ip6address=rdIp)
    except ObjectDoesNotExist:
        # the timedelta is a 
        # workaround to prevent the periodic process disabling the resource 
        rdHost = Host.objects.create(ip6address=rdIp, 
                                     network=n, 
                                     lastSeen=datetime.now() + timedelta(days=100))
    try:
        Resource.objects.get(host=rdHost, uri="/rd")
    except ObjectDoesNotExist:
        Resource.objects.create(host=rdHost, uri="/rd")


class Vr(pResource):
    def __init__(self, name="VirtualResource"):
        super(Vr, self).__init__(name, visible=True, observable=False, allow_children=True)
        self.payload = "prova"

    def render_GET(self, request, query=None):
        return self.payload

    def render_PUT(self, request, payload=None, query=None):
        return payload
    def render_DELETE(self, request, query=None):
        return True
    def render_POST(self, request, payload=None, query=None):
        print 'creating a virtual resource'
        print 'payload = ', payload
        q = "?" + "&".join(query)
        res = Vr(name=payload)
        return {"Payload": payload, "Location-Query": q, "Resource": res}    

class RD(pResource):
    def __init__(self, name="StorageResource"):
        super(RD, self).__init__(name, visible=True, 
                                 observable=False, 
                                 allow_children=True)
        self.payload = "Resource Directory"

    def render_GET(self, request, query=None):
        return self.payload

    def render_PUT(self, request, payload=None, query=None):
        ipAddr = request.source[0]
        timestamp = payload
        print 'RD server, message from: ' + ipAddr + ' time = ' + timestamp        
        try:
            h = Host.objects.get(ip6address=ipAddr)
            h.lastSeen = datetime.now()
            h.active = True
            if int(timestamp) < h.keepAliveCount:
                Log.objects.create(log_type='registration', message=ipAddr)
            h.keepAliveCount = int(timestamp)
            h.save()
            tmp = Resource.objects.filter(host=h)
            if len(tmp) == 0:
                print 'The host has no resources.'
                try:
                    h.DISCOVER()
                except Exception:
                    pass
        except ObjectDoesNotExist: #the host does not exists, create a new Host
            h = Host(ip6address=ipAddr, lastSeen=datetime.now(), keepAliveCount=1)
            h.save()
            try:
                h.DISCOVER()
            except Exception:
                pass
            Log.objects.create(log_type='registration', message=ipAddr)
        return {"Payload": "ok"}
    def render_POST(self, request, payload=None, query=None):
        print 'creating a virtual resource'
        print 'payload = ', payload
        q = "?" + "&".join(query)
        res = Vr(name=payload)
        return {"Payload": payload, "Location-Query": q, "Resource": res}



class CoAPServer(CoAP): 
    def __init__(self, host, port):
        CoAP.__init__(self)
        self.add_resource('rd/', RD())
        print "CoAP Server start on " + host + ":" + str(port)
        #print(self.root.dump())
