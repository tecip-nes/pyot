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
import json
import logging

from celery.result import AsyncResult
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import HttpResponse, render
from django.template import Context

from pyot.Forms import *
from pyot.models import *
from pyot.resourceRepr import getRenderer
from pyot.tasks import *
from pyot.tools.utils import *


#@staff_member_required
def startServer(request, wid):
    try:
        net = Network.objects.get(id=wid)
        if net.pid:
            return HttpResponse("Already running")
        else:
            net.startRD()
            return HttpResponse("Started")
    except ObjectDoesNotExist:
        msg = 'worker is not in db'
        return HttpResponse(msg)


#@staff_member_required
def stopAllSubs():
    sublist = Subscription.objects.filter(active=True)
    # stop all active subscriptions
    for s in sublist:
        s.cancel_subscription()

#@staff_member_required
def stopServer(request, wid):
    logging.debug('stopping')
    try:
        net = Network.objects.get(id=wid)
        if not net.pid:
            return HttpResponse("not running")
        else:
            stopAllSubs()
            net.stopRD()

        all_hosts = Host.objects.all()
        for host in all_hosts:
            host.keepAliveCount = 0
            host.save()

        return HttpResponse("revoked")
    except ObjectDoesNotExist:
        return HttpResponse("No process to stop")
    except Exception:
        pass

def getServerStatus(request):
    if request.method != 'GET':
        response = 'Bad request, needs a GET method'
        return HttpResponseBadRequest(response)
    networks = Network.objects.all()
    status = get_celery_worker_status()
    l = []
    for net in networks:
        Id = str(net.id)
        host = net.hostname
        prefix = str(net.network)
        if net.pid:
            rstatus = AsyncResult(net.pid).status
        else:
            rstatus = 'not running'
        try:
            _e = status[host]
            wstatus = 'Connected'
            uriLink = '<input type="submit" value="START" onclick = "startCoap(' + Id + ');"/><input type="submit" value="STOP" onclick = "stopCoap(' + Id + ');"/>'
        except KeyError:
            wstatus = 'Disconnected'
            uriLink = ''
        sub = [host, prefix, uriLink, wstatus, rstatus]
        dic = {'cell': sub}
        l.append(dic)
    json_dict = {
        'page': 1,
        'total': 1,
        'rows': l
        }
    j = json.dumps(json_dict)
    return HttpResponse(j)


#@login_required
def hosts(request):
    return render(request, 'host_list.htm')


#@login_required
def hostsList(request):
    if request.method != 'GET':
        response = 'Bad request, needs a GET method'
        return HttpResponseBadRequest(response)
    sortname = request.GET.get('sortname', 'timeadded')
    sortorder = request.GET.get('sortorder', 'asc') # Ascending/descending
    page = request.GET.get('page', 1) # What page we are on
    rp = int(request.GET.get('rp', 15)) # Num requests per page
    order = ''
    if sortorder == 'desc':
        order = '-'
    obj = Host.objects.filter(active=True).values('id', 'ip6address', 'timeadded', 'lastSeen').order_by(order + sortname)
    p = Paginator(obj, rp)
    filteredHostList = p.page(page).object_list
    l = []
    for i in filteredHostList:
        Id = str(i['id'])
        date = i['timeadded'].strftime('%d %b %Y %H.%M:%S')
        lastSeen = i['lastSeen'].strftime('%d %b %Y %H.%M:%S')

        sub = [Id, i['ip6address'], date, lastSeen]
        dic = {'id': Id, 'cell': sub}
        l.append(dic)
    json_dict = {
        'page': page,
        'total': p.count,
        'rows': l
        }
    j = json.dumps(json_dict)
    return HttpResponse(j)

#@login_required
def resources(request):
    hostid = request.GET.get('id', '')

    if hostid == '':
        logging.debug('vuoto')
        allres = Host.objects.filter(active=True)
        if len(allres) > 0:
            j = 0
            out = ''
            for i in allres:
                if j != 0:
                    out = out + ',' + str(i.id)
                else:
                    out = out + str(i.id)
                j += 1
            hostid = out
    c = Context({'listVar': hostid})
    return render(request, 'resource_list.htm', c)


#@login_required
def resourceList(request):
    hostidList = None
    query = request.GET.get('query', '')
    querytype = request.GET.get('qtype', '')
    page = request.GET.get('page', 1) # What page we are on
    rp = int(request.GET.get('rp', 15)) # Num requests per page

    if querytype == 'id' and query != '':
        hostidList = query.split(',')
    if hostidList == None:
        return HttpResponse('')
    for i in hostidList:
        logging.debug('retrieving resource ' + i)
    resObj = Resource.objects.filter(host__id__in=hostidList,
                                     host__active=True) # eccezioni per la query
    p = Paginator(resObj, rp)
    filteredResList = p.page(page).object_list
    l = []
    for i in filteredResList:
        Id = str(i.id)
        uriLink = '<div class="fake_link" onclick = "gotoRes('+ Id +');">' + i.uri + '</div >'
        sub = [Id, uriLink, str(i.host.ip6address), i.title]
        dic = {'id': Id, 'cell': sub}
        l.append(dic)
    json_dict = {
        'page': page,
        'total': p.count,
        'rows': l
        }
    j = json.dumps(json_dict)
    return HttpResponse(j)

#@login_required
def resourcePage(request, rid):
    try:
        r = Resource.objects.get(id=rid)
    except Resource.DoesNotExist:
        raise Http404
    resObj = getRenderer(r)
    c, t = resObj.getTemplate(request)
    return render(request, t, c)

def resourceStatus(request, rid):
    try:
        #rid =self.kwargs['rid']
        r = Resource.objects.get(id=rid)
        if r.host.active == True:
            status = "CONNECTED"
        else:
            status = "DISCONNECTED, last seen on: " + r.host.lastSeen.strftime(TFMT)
        return HttpResponse(status)
    except Resource.DoesNotExist:
        resp = 'The resource with id= ' + str(rid) + ' does not exist anymore'
        return HttpResponse(resp)


#@login_required
def obsList(request):
    rid = request.GET['query']
    sortname = request.GET.get('sortname', 'timeadded')
    sortorder = request.GET.get('sortorder', 'asc') # Ascending/descending
    page = request.GET.get('page', 1) # What page we are on
    rp = int(request.GET.get('rp', 15)) # Num requests per page
    order = ''
    if sortorder == 'desc':
        order = '-'
    messList = CoapMsg.objects.filter(resource__id=rid).exclude(sub=None).order_by(order + sortname)
    p = Paginator(messList, rp)
    filteredMessList = p.page(page).object_list
    l = []
    for i in filteredMessList:
        Id = str(i.id)
        date = i.timeadded.strftime('%d %b %Y %H.%M:%S')
        sub = [Id, date, i.payload]
        dic = {'id': Id, 'cell': sub}
        l.append(dic)
    json_dict = {
        'page': page,
        'total': p.count,
        'rows': l
        }
    j = json.dumps(json_dict)
    return HttpResponse(j)


#@staff_member_required
def settings(request):
    return render(request, 'settings.htm')

def obsLast(request, rid):
    try:
        s = Subscription.objects.filter(resource__id=rid, active=True).values('id').iterator()
        a = []
        for i in s:
            a.append(i['id'])
            logging.debug(i)

        maxID = CoapMsg.objects.filter(resource=rid, sub__in=a).aggregate(Max('id'))
        lastMsg = CoapMsg.objects.get(resource=rid, id=maxID['id__max'])
        r = lastMsg.payload
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        r = 'none'
    return HttpResponse(r)



#@login_required
def subList(request, rid):
    try:
        sub = Subscription.objects.filter(resource__id=rid, active=True)
        if sub.count():
            active = True
        else:
            active = False
        c = Context({'subList': sub, 'active': active})
        return render(request, 'sub_list.htm', c)
    except Subscription.DoesNotExist:
        raise Http404


#@staff_member_required
def cancelSub(request):
    pid = request.GET.get('pid', '')
    try:
        s = Subscription.objects.get(pid=pid)
        s.cancel_subscription()
        return HttpResponse('ok task revoked')
    except Subscription.DoesNotExist:
        raise Http404


#@login_required
def opRes(request):
    try:
        rid = request.GET.get('id', '')
        payload = request.GET.get('pd', None)
        operation = request.GET.get('op', '')
        try:
            r = Resource.objects.get(id=rid)
        except ObjectDoesNotExist:
            return HttpResponse('Resource not found')
        if operation == 'GET':
            if payload:
                payload = payload.encode("utf-8")
            res = r.GET(payload)
        elif operation == 'PUT':
            res = r.PUT(payload)
        elif operation == 'POST':
            res = r.POST(payload)
        else:
            return HttpResponse('Method unsupported')
        out = "%s %s" % (res.code, res.content)
        return HttpResponse(out)
    except Exception as e:
        return HttpResponse('Error, exception %s' % e)


#@staff_member_required
def observe(request):
    try:
        rid = request.GET.get('id', '')
        duration = request.GET.get('duration', '30')
        handler = request.GET.get('handler', '')
        renew = request.GET.get('renew', 'false')

        if handler == 'undefined':
            handler = None
        if duration == '':
            nduration = 30
        else:
            nduration = int(duration)
        if nduration < 0:
            nduration = 0
        if renew == 'false':
            renew = False
        else:
            renew = True

        out = 'starting observe on resource ' + rid + ' with duration ' + str(nduration)
        try:
            r = Resource.objects.get(id=rid)
            r.OBSERVE(nduration, handler, renew=renew)
        except ObjectDoesNotExist:
            return HttpResponse('Resource not found')
        return HttpResponse(out)
    except Exception as e:
        return HttpResponse('Error, exception %s' % e)


def getHandlerContext():
    try:
        handlersMsg = EventHandlerMsg.objects.filter(active=True)
    except Exception:
        handlersMsg = None

    r = Resource.objects.all()
    msgForm = MsgHandlerForm(initial={'resourceSel': r})
    c = Context({'msghandlers': handlersMsg,
                 'msgForm': msgForm})
    return c

#@login_required
def handlers(request):
    if request.method == 'POST':
        MsgForm = MsgHandlerForm(request.POST)
        if MsgForm.is_valid():
            try:
                res = Resource.objects.get(id=MsgForm.cleaned_data['Resource'].id)
            except ObjectDoesNotExist as e:
                return HttpResponse(e)
            m = CoapMsg.objects.create(resource=res,
                                       method=MsgForm.cleaned_data['Method'],
                                       payload=MsgForm.cleaned_data['Payload'])
            EventHandlerMsg.objects.create(msg=m,
                                           description=MsgForm.cleaned_data['Description'],
                                            max_activations=MsgForm.cleaned_data['MaxActivations'])
            logging.warning('MessageFormValid')
            c = getHandlerContext()
            return render(request, 'handlers.htm', c)
    c = getHandlerContext()
    return render(request, 'handlers.htm', c)


#@login_required
def remHandler(request, hid):
    try:
        ob = EventHandler.objects.get(id=hid, active=True)
        associatedSubs = Subscription.objects.filter(handler=ob, active=True)
        if associatedSubs.count() != 0:
            return HttpResponse('Active Subscriptions are using this handler!')
        associatedSubs = Subscription.objects.filter(handler=ob, active=False)
        if associatedSubs.count() != 0:
            # we have subscriptions associated, but not active
            ob.active = False
            ob.save()
            return HttpResponseRedirect(reverse('pyot.views.handlers'))
        else:
            # we don't have any subscription associated
            ob.delete()
            return HttpResponseRedirect(reverse('pyot.views.handlers'))
    except Exception:
        return HttpResponse('Error, unable to remove this handler')


#@staff_member_required
def startPing(request, hid):
    h = Host.objects.get(id=hid)
    res = h.PING()
    return HttpResponse(res)

#@staff_member_required
def pingPage(request):
    template = 'ping.htm'
    r = Resource.objects.filter(uri='MOBILE')
    l = []
    for res in r:
        l.append(res.host.ip6address)
    try:
        hosts = Host.objects.exclude(ip6address__in=l)
    except Exception:
        hosts = None
    c = {'hosts': hosts}
    return render(request, template, c)


