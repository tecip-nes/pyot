from tres_pymite import *
i = getInputList()
print "list:",
print len(i), i
if len(i) != 0:
  a = sum(i) / len(i)
  setOutput(a)
  print a
