'''
Created on Jul 29, 2014

@author: andrea
'''

from pyot.models.rest import Resource, Host
from pyot.models.virtualres import PeriodicVsT
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist

RDPATH = '/rd/'

def resource_template(**kwparams):
    """
    Returns the dictionary to be serialized as input/output Set.
    Will raise an exception if the parameters do not match the resource
    attributes.
    """
    Resource.objects.filter(**kwparams)
    return kwparams

def get_rd_host():
    try:
        host = Host.objects.get(ip6address='::1')
    except ObjectDoesNotExist:
        # @timedelta: workaround to prevent the host from being disabled by the periodic task
        host = Host.objects.create(ip6address='::1',
                                lastSeen=datetime.now() + timedelta(days=1000))
    return host

class PeriodicVsTemplate(object):
    """
    TODO
    """

    vst = None

    def __init__(self, input_template, name='perT'):
        """ 
        creates the template
        serve un host per istanziare una risorsa. per ora ne creo uno fasullo
        nella versione finale l'host potrebbe essere scelto in base alle risorse selezionate
        oppure semplicemente associato ad un unico host che ospita l'rdep
        """

        self.vst = PeriodicVsT.objects.create(host=get_rd_host(),
                                              ioSet=input_template,
                                              uri=RDPATH+name,
                                              title=name,
                                              rt='virtual template')

    def GET(self):
        return self.vst.GET()
    def POST(self, name):
        return self.vst.POST(name)
