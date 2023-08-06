from prdg.ploneio.interfaces.base import IContextAndRequestAware
from zope.interface import implements

class ContextAndRequestAware(object):
    implements(IContextAndRequestAware)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request