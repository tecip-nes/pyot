'''
Copyright (C) 2012,2013 Scuola Superiore Sant'Anna (http://www.sssup.it) 
and Consorzio Nazionale Interuniversitario per le Telecomunicazioni 
(http://www.cnit.it).

This file is part of PyoT, an IoT Django-based Macroprogramming Environment.

PyoT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
  
PyoT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with PyoT.  If not, see <http://www.gnu.org/licenses/>.

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
    
