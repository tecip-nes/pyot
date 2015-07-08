from tres_pymite import *

class state:
  def __init__(self):
    self.s1 = -1
    self.s2 = -1

print "Compound Event:",
s = getState(state)
x = getIntInput()
tag = getInputTag()
if tag == "sens_A":
  s.s1 = x
if tag == "sens_B":
  s.s2 = x
if (s.s1 >= 0) and (s.s2 >= 0):
  if s.s1 > s.s2:
    print "sens_A > sens_B"
    setOutput("sens_A > sens_B")
  else:
    print "sens_A <= sens_B"
saveState(s)
