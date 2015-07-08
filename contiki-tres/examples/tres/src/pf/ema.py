from tres_pymite import *

class state:
  def __init__(self):
    self.m = 0.0

print "Exponential Moving Average:",
s = getState(state)
x = getFloatInput()
s.m = 0.1 * x + 0.9 * s.m
print s.m
setOutput(s.m)
saveState(s)
