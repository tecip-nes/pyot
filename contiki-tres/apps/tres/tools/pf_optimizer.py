#!/usr/bin/env python2.6                                                         

import sys
import ast
import codegen
import optparse

################################################################################
#                                  Defines                                     #
################################################################################
GET_STATE = "getState"
SAVE_STATE = "saveState"
POP = "pop"
PUSH = "push"




################################################################################
#                             Class definitions                                #
################################################################################

# this class represents field transformation data
class FieldTrans:
  def __init__(self, var, val):
    self.var = var
    self.val = val

# this class finds the state class and variable
class StateClassVarFinder(ast.NodeVisitor):

  def __init__(self):
    self.state_class = None
    self.state_var = None

  def visit_Assign(self, assign_node):
    if type(assign_node.value) is ast.Call:
      call_node = assign_node.value
      if type(call_node.func) is not ast.Name:
        return
      if (call_node.func.id == GET_STATE):
        #print "Call: " + call_node.func.id + "\tArgs:",
        self.state_class = call_node.args[0].id
        self.state_var = assign_node.targets[0].id

# this NodeVisitor finds the ClassDef Node defining the state class
class StateClassFinder(ast.NodeVisitor):
  def __init__(self, state_class_name):
    self.state_class_name = state_class_name
    self.state_class_node = None

  def visit_ClassDef(self, class_node):
    if class_node.name == self.state_class_name:
      self.state_class_node = class_node

# this NodeVisitor finds the ClassDef Node defining the state class
class StateInstanceTransformer(ast.NodeTransformer):
  def __init__(self, class_node, state_var, state_fields_dict):
    self.class_node = class_node
    self.state_var = state_var
    self.state_fields_dict = state_fields_dict

  def visit_ClassDef(self, node):
    if node is self.class_node:
      return None
    self.generic_visit(node)
    return node

  def visit_Assign(self, assign_node):
    if type(assign_node.value) is ast.Call:
      call_node = assign_node.value
      if (call_node.func.id == GET_STATE):
        l = []
        for f in self.state_fields_dict.keys():
          node = ast.Assign()
          node.targets = [ ast.Name(id = self.state_fields_dict[f].var, ctx = ast.Load) ]
          func = ast.Call()
          func.func = ast.Name(id = POP, ctx = ast.Load)
          func.args = [ ast.Num(n = self.state_fields_dict[f].val) ]
          node.value = func
          l.append(node)
        return l
    self.generic_visit(assign_node)
    return assign_node

  def visit_Call(self, call_node):
    if call_node.func.id == SAVE_STATE:
      l = []
      for f in self.state_fields_dict.keys():
        func = ast.Call()
        func.func = ast.Name(id = PUSH, ctx = ast.Load)
        func.args = [  ast.Name(id = self.state_fields_dict[f].var, ctx = ast.Load) ]
        l.append(ast.Expr(value = func))
      return l
    self.generic_visit(call_node)
    return call_node 

  def visit_Attribute(self, attr_node):
    if attr_node.value.id == self.state_var:
      for f in self.state_fields_dict.keys():
        if attr_node.attr == f:
          return ast.Name(id = self.state_fields_dict[f].var, ctx = ast.Load())
    self.generic_visit(attr_node)
    return attr_node

################################################################################
#                            Function definitions                              #
################################################################################
def getClassFields(class_node):
  exec codegen.to_source(class_node)
  m = sys.modules[__name__]
  st = getattr(m, class_node.name)()
  print st.__dict__.keys()


################################################################################
#                                 Script body                                  #
################################################################################

# PARSE OPTIONS
parser = optparse.OptionParser()
parser.add_option("-i", "--input", metavar="FILE", dest="input_file", 
    help="input script")
parser.add_option("-o", "--output", metavar="FILE", dest="output_file", 
    help="output script (default: %default)", default="pf.py")

options, args = parser.parse_args()
if options.input_file is None:
  parser.print_help()
  exit(-1)

# OPEN INPUT SCRIPT
try:
  f = open(options.input_file)
  code = f.read()
  f.close()
except IOError:
  print "Error: can\'t open file " + options.input_file
  exit(-1)

# PARSE TREE
tree = ast.parse(code)

# FIND STATE CLASS NAME AND VARIABLE
parser = StateClassVarFinder()
parser.visit(tree)
state_class_name = parser.state_class
state_var_name = parser.state_var
if (state_class_name is None) or (state_var_name is None):
  print "No state class/variable found. Exiting..."
  exit(0)
print "State Found" + " (class = " + state_class_name +                          \
    "; variable = " + state_var_name + ";", 

# FIND STATE DEF_CLASS NODE
classFinder = StateClassFinder(parser.state_class)
classFinder.visit(tree)
class_node = classFinder.state_class_node

# FIND DATA FIELDS OF STATE CLASS AND THEIR DEFAULT VALUES
exec codegen.to_source(class_node)
m = sys.modules[__name__]
st = getattr(m, class_node.name)()
st_fields = st.__dict__.keys()
st_fields_def_values = st.__dict__
print "fields = " + str(st_fields) + ")"

# CREATE TRANSFORMATION DICTIONARY
st_fields_dict = dict()
c = ord('a')
for field in st_fields:
  print state_var_name + "." + field + "\t->\t" + '_' + chr(c)
  f = FieldTrans('_' + chr(c), st_fields_def_values[field])
  st_fields_dict[field] = f
  c = c + 1


# TRANSFORM STATE VAR
classFinder = StateInstanceTransformer(class_node, state_var_name, st_fields_dict)
classFinder.visit(tree)

# WRITE OUTPUT FILE
f = open(options.output_file, "w+")
f.write(codegen.to_source(tree) + "\n")
f.close()





#class FirstParser(ast.NodeVisitor):
#
#  def __init__(self):
#    pass
#
#  #def visit_BinOp(self, stmt_binop):
#    #for child in ast.iter_fields(stmt_binop):
#       #print 'child %s' % str(child)
#  def generic_visit(self, node):
#    print node
#    super(FirstParser, self).generic_visit(node)

#  def visit_Name(self, node):
#    print node.id


#def findInit(class_node):
#  for stmt in class_node.body:
#    if (type(stmt) is ast.FunctionDef) and (stmt.name.id == "__init__"):
#      return stmt
#
#def findClassFields(class_node):
#  init_method = findInit(class_node)
#  for stmt in init_method.body:
#    pass

#class StateClassFieldsFinder(ast.NodeVisitor):
#  def __init__(self, state_class):
#    self.state_class = state_class
#
#  def visit_ClassDef(self, class_node):
#    if class_node.name.id == self.state_class:
#      pass


