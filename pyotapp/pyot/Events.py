
from tasks import coapPut, coapGet, coapPost
'''
def sendScript(vm, script):
    res = coapSendScript.delay(vm, script)
    print 'res ',  res
    res.wait()
    return res.result     
'''    
    
def sendMsg(msg): 
    if msg.method == 'PUT':
        res = coapPut.delay(msg.resource.id, msg.payload)
        res.wait()
    if msg.method == 'POST':
        res = coapPost.delay(msg.resource.id, msg.payload)
        res.wait()
    if msg.method == 'GET':
        res = coapGet.delay(msg.resource.id) 
        res.wait()  
    return res.result       
    
