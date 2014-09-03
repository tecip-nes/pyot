'''
Created on Aug 21, 2014

@author: andrea
'''


input_list = None
output_result = None
actuator_setpoint = None

def get_input_list():
    return input_list
    
def set_output(out):
    global output_result
    output_result = out
    
def get_actuator_setpoint():
    return int(actuator_setpoint)

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
    return output_result, actuator_setpoint


    

""" Virtual Sensor pf example    
input = get_input_list()
if len(input) != 0:
  print input
  output = sum(input)/len(input)
  set_output(output)
"""

""" Virtual Actuator pf example    
input = get_input_list()
setpoint = get_actuator_setpoint()
if len(input) > 0:
  newSetpoint = setpoint / len(input)
  print input
  set_actuator(newSetpoint)
  set_output(newSetpoint)
"""