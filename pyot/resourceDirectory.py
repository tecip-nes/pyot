'''
Created on Aug 6, 2014

@author: andrea
'''

from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist

from coapthon2.resources.resource import Resource as pResource
from coapthon2.server.coap_protocol import CoAP
from pyot.models import Resource, Host, Log


def trunc_exc(exc, max_len=20):
    s = str(exc)
    return s[0:max_len] + '...'


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


class VrSubresource(pResource):
    def __init__(self, name="VirtualResource"):
        super(VrSubresource, self).__init__(name, visible=True,
                                            observable=False,
                                            allow_children=True)
        self.payload = "Virtual subResource (cfg)"

    def render_GET(self, request, query=None):
        uri = '/' + request.uri_path
        return str(Resource.objects.get(uri=uri).GET())

    def render_PUT(self, request, payload=None, query=None):
        uri = '/' + request.uri_path
        try:
            if payload is not None:
                Resource.objects.get(uri=uri).PUT(payload)
                return 'Resource updated'
            return 'Resource unmodified'
        except Exception as exc:
            return trunc_exc(exc)
    """
    def render_DELETE(self, request, query=None):
        #It is only possible to delete a resource if it has no subresources.
        try:
            uri = '/' + request.uri_path
            r = SubResource.objects.get(uri=uri)
            #sub_res = r.getSubResources()
            #if len(sub_res) == 0:
            r.delete()
            return True
            #else:
            #    return False
        except Exception:
            return False
    """


class VrInstance(pResource):
    def __init__(self, name="VirtualResource"):
        super(VrInstance, self).__init__(name,
                                         visible=True,
                                         observable=False,
                                         allow_children=True)
        self.payload = "Virtual Resource Instance"

    def render_GET(self, request, query=None):
        uri = '/' + request.uri_path
        return str(Resource.objects.get(uri=uri).GET())

    def render_PUT(self, request, payload=None, query=None):
        uri = '/' + request.uri_path
        try:
            if payload is not None:
                result = Resource.objects.get(uri=uri).PUT(payload)
                return {"Payload": result}
            return 'Resource unmodified'
        except Exception as exc:
            return trunc_exc(exc)
    """
    def render_DELETE(self, request, query=None):
        #It is only possible to delete a resource if it has no subresources.
        try:
            uri = '/' + request.uri_path
            r = VirtualSensorI.objects.get(uri=uri)
            sub_res = r.getSubResources()
            if len(sub_res) == 0:
                r.delete()
                return True
            else:
                return False
        except Exception:
            return False
    """
    def render_POST(self, request, payload=None, query=None):
        # currently meaningful only for internal (shell) requests
        print 'creating a virtual subresource'
        print 'payload = ', payload
        q = "?" + "&".join(query)
        res = VrSubresource(name=payload)
        return {"Payload": payload, "Location-Query": q, "Resource": res}


class VrTemplate(pResource):
    def __init__(self, name="VirtualResource"):
        super(VrTemplate, self).__init__(name,
                                         visible=True,
                                         observable=False,
                                         allow_children=True)
        self.payload = "Virtual Resource Template"

    def render_GET(self, request, query=None):
        """
        Usually returns the description of the virtual resource template.
        """
        uri = '/' + request.uri_path
        try:
            return str(Resource.objects.get(uri=uri).GET())
        except Exception as exc:
            return trunc_exc(exc)

    def render_POST(self, request, payload=None, query=None):
        # currently meaningful only for internal (shell) requests
        print 'creating a virtual resource instance'
        print 'payload = ', payload
        q = "?" + "&".join(query)
        res = VrInstance(name=payload)
        return {"Payload": payload, "Location-Query": q, "Resource": res}


class RD(pResource):
    def __init__(self, name="StorageResource"):
        super(RD, self).__init__(name, visible=True,
                                 observable=False,
                                 allow_children=True)
        self.payload = "Resource Directory"

    def render_GET(self, request, query=None):
        return {"Payload": "Resource Directory"}

    def render_PUT(self, request, payload=None, query=None):
        """
        Process keep-alive messages from CoAP Endpoints. The payload is a
        counter incremented every 10 seconds by the endpoints. If it is less
        than the stored keepAliveCount we consider the message as a
        registration. This way we can detect rebooting nodes.
        """
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
        except ObjectDoesNotExist:
            # the host does not exists, create a new Host
            h = Host.objects.create(ip6address=ipAddr,
                                    lastSeen=datetime.now(),
                                    keepAliveCount=1)
            try:
                h.DISCOVER()
            except Exception:
                pass
            Log.objects.create(log_type='registration', message=ipAddr)
        return {"Payload": "ok"}

    def render_POST(self, request, payload=None, query=None):
        # currently meaningful only for internal (shell) requests
        print 'creating a virtual resource template.'
        print 'payload = ', payload
        q = "?" + "&".join(query)
        res = VrTemplate(name=payload)
        return {"Payload": payload, "Location-Query": q, "Resource": res}


class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self)
        self.add_resource('rd/', RD())
        print "CoAP Server start on " + host + ":" + str(port)
