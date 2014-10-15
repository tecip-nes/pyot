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


def get_celery_worker_status():
    error_key = "ERROR"

    try:
        import celery
        insp = celery.task.control.inspect()
        d = insp.stats()
        if not d:
            d = {error_key: 'No running Celery workers were found.'}
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = {error_key: msg}
    except ImportError as e:
        d = {error_key: str(e)}
    return d


def clearTaskMeta():
    from djcelery.models import TaskMeta, states
    TaskMeta.objects.filter(status=states.SUCCESS).delete()


def get_statistics():
    #hosts = Host.objects.filter()
    #hostsactiveCount = Host.objects.filter(active=True).count()
    #resources = Resource.objects.filter(host__active=True).exclude(uri='.well-known')

    #hostcount = hosts.count()

    #rescount = resources.count()

    return {}
'''
    #server started
    now = datetime.now()
    try:
        server = RunningServer.objects.get()

        startT = server.timeadded
        starttime = startT.strftime(TFMT)
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
                  'lastSeen':lastSeen.strftime(TFMT),
                  'kacount': keepaliveCount,
                  'expected': expectedMessages,
                  'perc': perc}
            perHost.append(dic)
        perSub = []
        subs = Subscription.objects.filter(active=True)
        for s in subs:
            messcount = CoapMsg.objects.filter(sub = s).count()
            dic = {'res': s.resource,
                  'type': s.subtype,
                  'period': s.period,
                  'thr': s.threshold,
                  'timeadded':s.timeadded.strftime(TFMT),
                  'messcount': messcount}
            perSub.append(dic)
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
'''
