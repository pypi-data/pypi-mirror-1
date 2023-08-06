from zope.interface import implements

from Products.GenericSetup.interfaces import IExportContext
from Products.GenericSetup.context import BaseContext

class StringExportContext(BaseContext):
    implements(IExportContext)
    text = None

    def __init__(self, tool=None):
        BaseContext.__init__(self, tool, 'utf-8')
        self.text = []
        
        
    def writeDataFile(self, filename, text, content_type, subdir=None):
        self.text.append(text)
    
    def getString(self):
        return '/n'.join(self.text)