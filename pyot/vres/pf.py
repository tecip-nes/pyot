'''
Created on Aug 21, 2014

@author: andrea
'''


input_list = None
output_result = None

def get_input_list():
    return input_list
    
def set_output(out):
    global output_result
    output_result = out
    
    

def apply_pf(pf, il):
    global input_list 
    input_list = il
    print 'running the pf'
    exec(pf)
    global output_result
    return output_result
    