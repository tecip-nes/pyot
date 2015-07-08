Contiki with T-Res
============================

This fork of Contiki adds T-Res, a programming abstraction framework for
IoT-based WSNs. T-Res allows you to create simple "tasks", called T-Res tasks,
that can be installed in your IoT-based WSN at run-time.

A T-Res task is written in Python and allows a node to monitor one or more
sensors, process their data, and send the produced output to an actuator.
Alternatively, the produced output can be stored in a local resource that can
be observed by another node or the user. T-Res tasks can be used to implement
simple event-detection and control applications.

More information about T-Res can be found in the
[wiki](https://github.com/tecip-nes/contiki-tres/wiki) and in the following
paper:
> D. Alessandrelli, M. Petracca, and P. Pagano, “[T-Res: enabling 
reconfigurable in-network processing in IoT-based WSNs]
(http://retis.sssup.it/~daniele/t-res.pdf)”, in Proceedings of the 9th IEEE
International Conference on Distributed Computing in Sensor Systems (DCoSS'13)
and Workshops, Cambridge, MA, May 2013.

================================================================================

#### Acknowledgments

T-Res uses [PyMite](https://code.google.com/p/python-on-a-chip/) for 
interpreting Python bytecode. PyMite is a reduced Python virtual machine for
constrained devices developed by Dean Hall.
