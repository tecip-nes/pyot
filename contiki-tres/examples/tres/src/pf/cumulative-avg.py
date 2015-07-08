from tres_pymite import *

class state:
  def __init__(self):
    self.n = 0
    self.ca = 0.0

print "Cumulative Average"
s = getState(state)
x = getIntInput()
s.n += 1
s.ca += (x - s.ca) / s.n
setOutput(s.ca)
saveState(s)
