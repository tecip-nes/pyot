'''
Created on Aug 21, 2014

@author: andrea
'''


input_list = None
output_result = None
actuator_setpoint = None


def getInputList():
    return input_list


def setOutput(out):
    global output_result
    output_result = out


def getIntInput():
    return int(actuator_setpoint)


def getOdCount():
    try:
        print input_list
        l = len(input_list)
        return l
    except:
        return 0


def set_actuator(value):
    global actuator_setpoint
    actuator_setpoint = value


def apply_pf(pf, il):
    global input_list
    global actuator_setpoint
    input_list = il
    print 'running the pf'
    exec(pf)

    global output_result
    print output_result
    return output_result


# Examples of pf
_cmd = """
i = getIntInput()
print "in:", i
od = getOdCount()
setOutput(i/od)
"""

_aggr = """
from tres_pymite import *
i = getInputList()
print "list:",
print len(i), i
if len(i) != 0:
  a = sum(i) / len(i)
  setOutput(a)
  print a
"""
