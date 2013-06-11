'''
@author: Andrea Azzara' <a.azzara@sssup.it>
'''
import logging
from django.shortcuts import HttpResponse, render
from django.http import HttpResponseBadRequest
from tasks import *
from models import *
from celery.task.control import revoke 
from django.template import Context
from resourceRepr import getRenderer
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from Forms import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import simplejson
from datetime import datetime, timedelta
from celery.result import AsyncResult
from utils import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.utils.decorators import method_decorator        
from django_sse.views import BaseSseView
import time 

SSE_UPDATE_INTERVAL = 0.5

def SSE_SLEEP(interval=SSE_UPDATE_INTERVAL):
    time.sleep(interval)

def home(request):
    return render(request,'home.htm')

def contacts(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            sender = form.cleaned_data['sender']
            mess = 'Sender is ' + sender + '\n' + message            
            mail_admins(subject, mess, fail_silently=False, connection=None, html_message=None)
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = ContactForm() # An unbound form

    return render(request, 'contacts.htm', {
        'form': form,
    })

    return render(request,'contacts.htm')

#@login_required
def cam(request):
    return render(request,'cam.htm')

#@login_required
def myaccount(request):
    return render(request,'account.html')


#@login_required
def deleteUser(request):
    return render(request,'deleteuser.htm')

#@login_required
def confirmDeleteUser(request):
    request.user.delete()
    logout(request)
    return render(request,'home.htm')


#@staff_member_required
def settings(request):
    status = get_celery_worker_status()
    if 'ERROR' in status:
        msg = 'Workers error: ' + status['ERROR']
    else:
        msg = 'Workers status: OK' 
    status = {'status': msg}
    d =  get_statistics()
    cont = dict(status.items() + d.items())
    c = Context(cont)   
  
    return render(request,'settings.htm', c)

#@login_required
def req(request):
    if request.method == 'GET':
        try:
            addr = request.GET['addr']
            method = request.GET['id']
            payload = request.GET['pd']
        except Exception as _e:
            response = 'Bad request'
            return HttpResponse(response)        
        
        response = 'you requested method ' + method + ', to address ' + addr + ', with payload ' + payload
        return HttpResponse(response)
    else:
        response = 'Bad request'
        return HttpResponse(response)

#@staff_member_required
def startServer(request):
    try:
        _proc = RunningServer.objects.get()
        return HttpResponse("Already running")
    except ObjectDoesNotExist: 
        r = coapRdServer.delay()  
        server = RunningServer(pid=r.task_id)
        server.save()
        
        logging.debug('Saved in db')    
        logging.debug('task pid = ' + r.task_id)
        return HttpResponse(r.status)

#@staff_member_required
def stopServer(request):
    logging.debug('stopping') 
    try:   
        proc = RunningServer.objects.get()
        revoke(proc.pid, terminate=True)
        proc = RunningServer.objects.get()
        proc.delete() 
        hosts = Host.objects.all()
        for h in hosts:
            h.keepAliveCount = 0
            h.save()
        
        return HttpResponse("revoked")
    except ObjectDoesNotExist:    
        return HttpResponse("No process to stop")
    except Exception:
        pass

class getServerStatus(BaseSseView):
    
    #@method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(getServerStatus, self).dispatch(*args, **kwargs)    
    def iterator(self):
        while True:
            try:   
                proc = RunningServer.objects.get() 
                res = AsyncResult(proc.pid)  
                self.sse.add_message("serverStatus", res.status)
                SSE_SLEEP()
                yield                
            except ObjectDoesNotExist:    
                self.sse.add_message("serverStatus", "No RD server active")
                SSE_SLEEP()
                yield
            except Exception as e:
                logging.error(e)
            
#@login_required         
def hosts (request):
    return render(request, 'host_list.htm')


#@login_required 
def hostsList(request):
    if request.method != 'GET':
        response = 'Bad request, needs a GET method'
        return HttpResponseBadRequest(response)
    sortname = request.REQUEST.get('sortname', 'timeadded')
    sortorder = request.REQUEST.get('sortorder', 'asc') # Ascending/descending
    page = request.REQUEST.get('page', 1) # What page we are on
    rp = int(request.REQUEST.get('rp', 15)) # Num requests per page
    order = ''
    if sortorder == 'desc':
        order = '-'     
    obj = Host.objects.filter(active=True).values('id', 'ip6address', 'timeadded','lastSeen').order_by(order+sortname)
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
    json = simplejson.dumps(json_dict)        
    return HttpResponse(json) 

#@login_required 
def resources(request):
    hostid = request.REQUEST.get('id', '')
    
    if hostid == '':
        logging.debug('vuoto')
        allres = Host.objects.filter(active=True)
        if len(allres) > 0:
            j = 0
            out = ''
            for i in allres:
                if j != 0:
                    out = out + ','+ str(i.id)
                else:
                    out = out + str(i.id)   
                j += 1    
            hostid = out         
    c = Context({'listVar': hostid})   
    return render(request, 'resource_list.htm', c)


#@login_required 
def resourceList(request):
    hostidList = None
    query = request.GET['query']  #TODO gestione delle eccezioni, id non presenti
    querytype = request.GET['qtype']
    page = request.REQUEST.get('page', 1) # What page we are on
    rp = int(request.REQUEST.get('rp', 15)) # Num requests per page
    
    if (querytype == 'id' and query != ''):
        hostidList = query.split(',')
    if (hostidList == None ) :
        return HttpResponse('')      
    for i in hostidList:
        logging.debug('retrieving resource '+ i )
    resObj = Resource.objects.filter(host__id__in=hostidList, host__active=True) #eccezioni per la query
    p = Paginator(resObj, rp)
    filteredResList = p.page(page).object_list
    l = []
    for i in filteredResList:
        Id = str(i.id)
        uriLink = '<div class="fake_link" onclick = "gotoRes('+ Id +');">' + i.uri + '</div >'
        sub = [Id, uriLink, i.host.ip6address]
        dic = {'id': Id, 'cell': sub}
        l.append(dic)
    json_dict = {
        'page': page,
        'total': p.count,
        'rows': l
        }
    json = simplejson.dumps(json_dict)        
    return HttpResponse(json)   

#@login_required
def resourcePage(request, rid):
    try:
        r = Resource.objects.get(id=rid)
    except ObjectDoesNotExist:
        return HttpResponse('The resource with id= ' + str(rid) + ' does not exist anymore')  
    resObj= getRenderer(r)
    c, t = resObj.getTemplate(request)
    return render(request, t, c)

class resourceStatus(BaseSseView):
    #@method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(resourceStatus, self).dispatch(*args, **kwargs)    
    def iterator(self):
        while True:
            try:
                rid =self.kwargs['rid']
                r = Resource.objects.get(id=rid)
            except ObjectDoesNotExist:
                resp = 'The resource with id= ' + str(rid) + ' does not exist anymore' 
                self.sse.add_message("resStatus", resp)
                SSE_SLEEP()
                yield  
            if r.host.active == True:
                status = "CONNECTED"
                self.sse.add_message("resStatus", status)
                SSE_SLEEP()
                yield                    
            else:
                status = "DISCONNECTED, last seen on: " + r.host.lastSeen.strftime('%d %b %Y %H.%M:%S')
                self.sse.add_message("resStatus", status)
                SSE_SLEEP()
                yield                  

               
#@login_required 
def obsList(request):
    rid = request.GET['query']
    sortname = request.REQUEST.get('sortname', 'timeadded')
    sortorder = request.REQUEST.get('sortorder', 'asc') # Ascending/descending
    page = request.REQUEST.get('page', 1) # What page we are on
    rp = int(request.REQUEST.get('rp', 15)) # Num requests per page
    order = ''
    if sortorder == 'desc':
        order = '-'      
    messList = CoapMsg.objects.filter(resource__id=rid).exclude(sub=None).order_by(order+sortname)
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
    json = simplejson.dumps(json_dict)        
    return HttpResponse(json)


class pushUpdate(BaseSseView):
    '''
    triggers update on resource/host tables
    '''
    #@method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(pushUpdate, self).dispatch(*args, **kwargs)    
     
    
    def iterator(self):
        baseTime = datetime.now()
        while True:
            
            cid = self.kwargs['className']
            #print cid
            #tfmt = "%Y-%m-%d %H:%M:%S"
            try:
                t = ModificationTrace.objects.get(className=cid)
                if t.lastModified > baseTime:
                    baseTime = t.lastModified
                    #logging.error('T ' + t.lastModified.strftime(tfmt) + ' ' + baseTime.strftime(tfmt))
                    self.sse.add_message("pushUpdate", "T")
                    SSE_SLEEP()
                    yield
                else:
                    self.sse.add_message("pushUpdate", "F")
                    SSE_SLEEP()
                    yield                                           
            except ObjectDoesNotExist, MultipleObjectsReturned:
                self.sse.add_message("pushUpdate", "F")
                SSE_SLEEP()
                yield                         


class obsLast(BaseSseView):
    '''
    Stream observe values (only if new values arrived)
    '''   
    #@method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(obsLast, self).dispatch(*args, **kwargs)    
    def iterator(self):
        baseTime = datetime.now()
        while True:
            rid = self.kwargs['rid']
            try:
                s = Subscription.objects.filter(resource__id = rid, active = True).values('id').iterator()
                a = []
                for i in s:
                    a.append(i['id'])
                    logging.debug(i)
                maxID = CoapMsg.objects.filter(resource=rid, sub__in=a).aggregate(Max('id'))
                lastMsg = CoapMsg.objects.get(resource=rid, id = maxID['id__max'])
                if lastMsg.timeadded > baseTime:
                    r = lastMsg.payload
                    self.sse.add_message("obsLast", r)
                    SSE_SLEEP(1)
                    yield
                elif lastMsg.timeadded + timedelta(seconds=2) < datetime.now():     
                    r = 'none'    
                    self.sse.add_message("obsLast", r)   
                    SSE_SLEEP(1)
                    yield
                else:
                    SSE_SLEEP(1)
                    yield                
            except ObjectDoesNotExist, MultipleObjectsReturned:
                r = 'none'    
                self.sse.add_message("obsLast", r)
                SSE_SLEEP()
                yield    
            except Exception as e:
                logging.error(e)  

#@login_required 
def subList(request,rid):
    try:
        sub = Subscription.objects.filter(resource__id = rid, active = True)
        if sub.count():
            active = True
        else:
            active = False    
        c = Context({'subList': sub, 'active': active})   
        return render(request, 'sub_list.htm', c)    
    except ObjectDoesNotExist as e:
        return HttpResponse('Error, exception %s' % e)      


#@staff_member_required
def terminate(request):
    pid = request.REQUEST.get('pid', '')
    if pid == '':
        return HttpResponse('')
    logging.debug('PID =' + pid)
    #coapStopObserve.delay(pid)
    revoke(pid, terminate=True)
    s = Subscription.objects.get(pid=pid)
    s.active = False
    s.save()    
    return HttpResponse('ok task revoked')


#@login_required 
def opRes(request):
    try:
        rid = request.REQUEST.get('id', '')
        payload = request.REQUEST.get('pd', None)
        operation = request.REQUEST.get('op', '')
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
        out = str(res)
        return HttpResponse(out)
    except Exception as e:
        return HttpResponse('Error, exception %s' % e)  


#@staff_member_required       
def observe(request):
    try:
        rid = request.REQUEST.get('id', '')
        duration = request.REQUEST.get('duration', '30')
        handler = request.REQUEST.get('handler', '')
        
        if handler == 'undefined':
            handler = None
        if duration == '':
            nduration = 30
        else:
            nduration = int(duration)    
        if nduration < 0:
            nduration = 0
        out = 'starting observe on resource ' + rid + ' with duration '+ str(nduration) 
        try:
            r = Resource.objects.get(id=rid)
            r.OBSERVE(nduration, handler)
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
    msgForm = MsgHandlerForm(initial = {'resourceSel': r })
    c = Context({'msghandlers': handlersMsg, 
                 'msgForm': msgForm})
    return c    
   
#@login_required    
def handlers(request):
    if request.method == 'POST':
        MsgForm = MsgHandlerForm(request.POST)
        if MsgForm.is_valid():
            try:
                res = Resource.objects.get(id = MsgForm.cleaned_data['Resource'].id)
            except ObjectDoesNotExist as e:
                return HttpResponse(e)             
            m = CoapMsg.objects.create(resource = res, method = MsgForm.cleaned_data['Method'],
                        payload = MsgForm.cleaned_data['Payload'])
            EventHandlerMsg.objects.create(msg = m, description = MsgForm.cleaned_data['Description'], 
                                   max_activations=MsgForm.cleaned_data['MaxActivations'])
            logging.warning('MessageFormValid')
            c =  getHandlerContext()       
            return render(request, 'handlers.htm', c) 
    c =  getHandlerContext()       
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
            #we have subscriptions associated, but not active
            ob.active=False
            ob.save()
            return HttpResponseRedirect(reverse('pyot.views.handlers'))
        else:
            #we don't have any subscription associated
            ob.delete()
            return HttpResponseRedirect(reverse('pyot.views.handlers'))
    except Exception:
        return HttpResponse('Error, unable to remove this handler')  


#@staff_member_required
def startPing(request, hid):
    res = pingTest.delay(hid)
    res.wait()
    return HttpResponse(res.result)     

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

#@staff_member_required
def stopAllSubs():
    sublist = Subscription.objects.filter(active=True)
    #stop all active subscriptions
    for s in sublist:
        coapStopObserve.delay(str(s.pid))
  

#@staff_member_required     
def shutdown(request):
    try:
        stopAllSubs()
        #stop coap server
        stopServer(request)
        return HttpResponse('All processes are stopping')
    except Exception as e:
        return HttpResponse('Error, exception %s' % e)
        
