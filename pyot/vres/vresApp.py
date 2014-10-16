'''
Created on Jul 29, 2014

@author: andrea
'''

from datetime import datetime, timedelta

from pyot.models.rest import Resource, Host
from pyot.models.virtualres import VsT, VaT, VsHistT, VsPeriodicT


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
    # @timedelta: workaround to prevent the host from being disabled by
    # the periodic task
    future = datetime.now() + timedelta(days=1000)
    host, _created = Host.objects.get_or_create(ip6address=RD_DEFAULT_HOST,
                                                defaults={'lastSeen': future})
    return host


class VresTemplate(object):
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


class VsTemplate(VresTemplate):
    """
    TODO
    """
    def __init__(self, input_template, name='senT'):
        """
        """
        super(VsTemplate, self).__init__()
        rd_host = get_rd_host()
        self.vst, _created = VsT.objects.get_or_create(host=rd_host,
                                                       uri=RDPATH + name,
                                                       title=name,
                                                       rt=self.rt)
        self.vst.ioSet = input_template
        self.vst.save()


class VsPeriodicTemplate(VresTemplate):
    """
    TODO
    """
    def __init__(self, input_template, name='senT'):
        """
        """
        super(VsPeriodicTemplate, self).__init__()
        rd_host = get_rd_host()
        self.vst, _created = VsPeriodicT.objects.get_or_create(host=rd_host,
                                                               uri=RDPATH + name,
                                                               title=name,
                                                               rt=self.rt)
        self.vst.ioSet = input_template
        self.vst.save()


class VsHistTemplate(VresTemplate):
    """
    TODO
    """
    def __init__(self, input_template, name='senT'):
        """

        """
        super(VsHistTemplate, self).__init__()
        rd_host = get_rd_host()
        self.vst, _created = VsHistT.objects.get_or_create(host=rd_host,
                                                           uri=RDPATH + name,
                                                           title=name,
                                                           rt=self.rt)
        self.vst.ioSet = input_template
        self.vst.save()


class VaTemplate(VresTemplate):
    """
    TODO
    """
    def __init__(self, output_template, name='actT'):
        """
        creates the virtual actuator template
        """
        super(VaTemplate, self).__init__()
        rd_host = get_rd_host()
        self.vst, _created = VaT.objects.get_or_create(host=rd_host,
                                                       uri=RDPATH + name,
                                                       title=name,
                                                       rt=self.rt)
        self.vst.ioSet = output_template
        self.vst.save()
