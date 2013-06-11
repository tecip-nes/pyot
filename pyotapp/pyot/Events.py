'''
@author: Andrea Azzara' <a.azzara@sssup.it>
'''
from tasks import coapPut, coapGet, coapPost
    
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
    
