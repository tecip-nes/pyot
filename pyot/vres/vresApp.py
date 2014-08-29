'''
Created on Jul 29, 2014

@author: andrea
'''

from pyot.models.rest import Resource, Host
from pyot.models.virtualres import VirtualSensorT, VirtualActuatorT
from datetime import datetime, timedelta

RDPATH = '/rd/'

RD_DEFAULT_HOST = 'bbbb::1'

def resource_template(**kwparams):
    """
    Returns the dictionary to be serialized as input/output Set.
    Will raise an exception if the parameters do not match the resource
    attributes.
    """
    Resource.objects.filter(**kwparams)
    return kwparams

def get_rd_host():
    # @timedelta: workaround to prevent the host from being disabled by the periodic task
    future = datetime.now() + timedelta(days=1000)
    host, _created = Host.objects.get_or_create(ip6address=RD_DEFAULT_HOST,
                                      defaults={'lastSeen':future})   
    return host



class VirtualResourceTemplate(object):
    """
    TODO
    """
    vst = None
    rt = 'vrtemplate'
    def __init__(self):
        pass        
    def GET(self):
        return self.vst.GET()
    def POST(self, name):
        return self.vst.POST(name)

class VirtualSensorTemplate(VirtualResourceTemplate):
    """
    TODO
    """
    def __init__(self, input_template, name='senT'):
        """ 
        creates the template
        serve un host per istanziare una risorsa. per ora ne creo uno fasullo
        nella versione finale l'host potrebbe essere scelto in base alle risorse selezionate
        oppure semplicemente associato ad un unico host che ospita l'rdep
        """
        super(VirtualSensorTemplate, self).__init__()
        rd_host = get_rd_host()
        self.vst, _created = VirtualSensorT.objects.get_or_create(host=rd_host,
                                                     uri=RDPATH+name,
                                                     title=name,
                                                     rt=self.rt)
        self.vst.ioSet = input_template
        self.vst.save()


    
class VirtualActuatorTemplate(VirtualResourceTemplate):
    """
    TODO
    """
    def __init__(self, output_template, name='actT'):
        """ 
        creates the template
        serve un host per istanziare una risorsa. per ora ne creo uno fasullo
        nella versione finale l'host potrebbe essere scelto in base alle risorse selezionate
        oppure semplicemente associato ad un unico host che ospita l'rdep
        """
        super(VirtualActuatorTemplate, self).__init__()        
        rd_host = get_rd_host()
        self.vst, _created = VirtualActuatorT.objects.get_or_create(host=rd_host,
                                                     uri=RDPATH+name,
                                                     title=name,
                                                     rt=self.rt)
    
