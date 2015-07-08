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
from django.db import models
from pyot.models.rest import Resource, Network, Host, Response, SUCCESS, FAILURE, CONTENT
from pyot.models.tres import TResProcessing, TResT
from pyot.models.rpl import RplGraph
from django.core.validators import validate_slug
from networkx.algorithms import bfs_successors


class TResDeployFailure(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class pyMap(models.Model):
    """
    Defines a PyoT map function.
    """
    timeAdded = models.DateTimeField(auto_now_add=True, blank=True)
    name = models.CharField(max_length=10, validators=[validate_slug],
                            default='map', null=True)
    inputS = models.ManyToManyField(Resource, related_name='inputResources')
    description = models.CharField(max_length=500, blank=True, null=True)
    period = models.IntegerField(default=0)

    class Meta(object):
        app_label = 'pyot'

    def __unicode__(self):
        return u"{n} -- inputs={i} -- period={t}".format(n=self.name,
                                                   i=str(self.inputS.all()),
                                                   t=self.period)

MAPREDUCE_STATES = (
    (u'CREATED', u'CREATED'),
    (u'INSTALLED', u'INSTALLED'),
    (u'RUNNING', u'RUNNING'),
    (u'STOPPED', u'STOPPED'),
    (u'CLEARED', u'CLEARED'),
)


class pyMapReduce(models.Model):
    """
    Defines a PyoT MapReduce function.
    """
    timeAdded = models.DateTimeField(auto_now_add=True, blank=True)
    pmap = models.ForeignKey(pyMap, related_name='map')
    preduce = models.ForeignKey(TResProcessing, related_name='reducer')
    output = models.ForeignKey(Resource, related_name='output')
    min_input = models.IntegerField(default=2)

    network = models.ForeignKey(Network, null=True,
                                related_name='net')

    tresTasks = models.ManyToManyField(TResT, related_name='tresTasks')

    state = models.CharField(max_length=10,
                             blank=False,
                             choices=MAPREDUCE_STATES,
                             default='CREATED')

    class Meta(object):
        app_label = 'pyot'

    def __unicode__(self):
        return u"map = {m}\nreduce = {r}\noutput = {o}\nstate = {s}".format(m=self.pmap,
                                                                    r=self.preduce,
                                                                    o=self.output,
                                                                    s=self.state)

    def deploy(self, net):
        """
        TODO
        """
        print 'Deploy mapReduce task:\n\n' + self.__unicode__() + '\n\n...on network: ' + str(net)

        try:
            g = RplGraph.objects.filter(net=net)[0]
        except:
            g = net.rplDagUpdate()

        gra = g.getGraph()

        # at the beginning the list of input nodes is only made of 'sensor' resources
        resource_id_list = set([r.id for r in self.pmap.inputS.all()])

        reducers_id_list = []

        tres_nodes = Resource.objects.filter(uri='/tasks', host__network=net)
        tres_nodes_ids = [tres.host.id for tres in tres_nodes]

        nodes_of_interest = bfs_successors(gra, '6LBR')
        noi_len = len(nodes_of_interest)

        print '\nBfs successors 6lbr'
        for i, j in enumerate(nodes_of_interest): # we start from the bottom of the graph, ignoring leaf nodes

            host = g.find_host_from_node(j)

            if host is None:
                continue
            # Skip the node if it is not a t-res node
            if host.id not in tres_nodes_ids:
                continue

            try:
                desc_list = g.get_descendants(host)
            except:
                continue
            # get the list of descendants' node id
            descendant_ids = [g.find_host_from_node(n).id for n in desc_list]
            # consider also the node itself as a possible input node
            descendant_ids.append(host.id)
            # we get the list of descendant hosts
            descendant_hosts = Host.objects.filter(id__in=descendant_ids)

            # now we have to count the number of input resources in the list of descendant nodes
            descendant_inputs = Resource.objects.filter(id__in=list(resource_id_list), host__in=descendant_hosts) # select
            print 'Visiting host', host, '-->', descendant_inputs, descendant_inputs.count(), 'inputs'

            try:
                if descendant_inputs.count() >= self.min_input:
                    print '**** Allocating a reducer on ', host
                    selected_inputs_ids = set([inp.id for inp in descendant_inputs])
                    print 'selected inputs', descendant_inputs

                    out = None
                    if i == noi_len - 2:
                        out = self.output
                    # create the TresTask object
                    tresTask = TResT.objects.create(pf=self.preduce,
                                                    output=out,
                                                    period=self.pmap.period)

                    for inp in descendant_inputs:
                        tresTask.inputS.add(inp)
                    tresTask.save()

                    # deploy the t-res task on the host
                    tres_node = Resource.objects.get(uri='/tasks', host=host)
                    result = tresTask.deploy(tres_node)
                    if result.code != SUCCESS:
                        raise TResDeployFailure('Error installing reduce task: ' + str(tresTask))

                    self.tresTasks.add(tresTask)
                    self.save()

                    # get the new last output resource reference
                    lo = tresTask.getLastOutput()

                    # remove the input resources we just assigned to the reducer
                    resource_id_list.difference_update(selected_inputs_ids)

                    # add the newly created reducer to the list of input resources (t-res lo)
                    resource_id_list.add(lo.id)

                    # update the list of reducers
                    reducers_id_list.append(host.id)
                print
            except TResDeployFailure as e:
                # rollback, uninstall tasks!
                print 'rollbacking'
                res = self.uninstall()
                if res.code == FAILURE:
                    m = ' Failed uninstalling already deployed reducers'
                else:
                    m = ' Rollback successful'
                return Response(FAILURE, str(e) + m)
        self.state = 'INSTALLED'
        self.save()
        return Response(SUCCESS, 'Successfully installed mapreduce task on network' + str(net))

    def get_reducer_hosts(self):
        if self.state in ['CREATED', 'CLEARED']:
            return []
        reducers_id_list = [task.TResResource.host.id for task in self.tresTasks.all()]
        reducer_hosts = Host.objects.filter(id__in=reducers_id_list)
        return reducer_hosts

    def uninstall(self):
        for task in self.tresTasks.all():
            if task.state == 'CREATED':
                print 'this task is not installed: ' + str(task)
                continue
            result = task.uninstall()
            if result.code != SUCCESS:
                return Response(FAILURE, 'Error uninstalling reduce task: ' + str(task))
            else:
                print 'Successfully removed task: ' + str(task)
                self.tresTasks.remove(task)
                self.save()
            self.tresTasks.clear()
            self.save()
        return Response(SUCCESS, 'PyoT mapreduce process successfully uninstalled')

    def start(self):
        for task in self.tresTasks.all():
            result = task.start()
            if result.code != CONTENT:
                return Response(FAILURE, 'Error starting reduce task: ' + str(task) + result.content)
        return Response(SUCCESS, 'PyoT mapreduce process successfully started')

    def stop(self):
        for task in self.tresTasks.all():
            result = task.stop()
            if result.code != CONTENT:
                return Response(FAILURE, 'Error stopping reduce task: ' + str(task) + result.content)
        return Response(SUCCESS, 'PyoT mapreduce process successfully stopped')
