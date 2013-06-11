from django.template import Context
from models import *

class generic():
	template = 'resource.htm'
	def __init__(self, rid):
		logging.debug("Generic resource")
		self.c = {'rid': rid.id, 'uri':rid.uri, 'ip': rid.host.ip6address, 'hid': rid.host.id}
	def getTemplate(self, request):
		return Context(self.c), self.template

		
class observable(generic):
	template = 'observable_template.htm'
	def __init__(self, rid):
		generic.__init__(self, rid)	#Super
		try:
			handlers = EventHandler.objects.filter(active=True)
		except Exception:
			handlers = None
		c2 = {'handlers': handlers}
		self.newContext = dict(self.c.items() + c2.items())					
	def getTemplate(self, request):
		return Context(self.newContext), self.template			
	
def getRenderer(rid):
	if rid.obs:
		return observable(rid)
	else:
		return generic(rid)

