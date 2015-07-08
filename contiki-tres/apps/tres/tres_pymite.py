"""__NATIVE__
#include <tres-pymite.h>
"""

def setOutput(out):
  """__NATIVE__
  return tres_pm_set_output(ppframe); 
  """

def getInput():
  """__NATIVE__
  return tres_pm_get_input(ppframe); 
  """

def getInputTag():
  """__NATIVE__
  return tres_pm_get_input_tag(ppframe); 
  """

def getInputList():
  """__NATIVE__
  return tres_pm_get_input_list(ppframe); 
  """

def getIntInput():
  """__NATIVE__
  return tres_pm_get_int_input(ppframe); 
  """

def getFloatInput():
  """__NATIVE__
  return tres_pm_get_float_input(ppframe); 
  """

def getOdCount():
  """__NATIVE__
  return tres_pm_get_od_count(ppframe); 
  """

def _getState(cli):
  """__NATIVE__
  return tres_pm_get_state(ppframe); 
  """

def getState(cl):
  return _getState(cl())

def saveState(cli):
  """__NATIVE__
  return tres_pm_save_state(ppframe); 
  """

def pop(def_val):
  """__NATIVE__
  return tres_pm_state_pop(ppframe); 
  """

def push(val):
  """__NATIVE__
  return tres_pm_state_push(ppframe); 
  """

