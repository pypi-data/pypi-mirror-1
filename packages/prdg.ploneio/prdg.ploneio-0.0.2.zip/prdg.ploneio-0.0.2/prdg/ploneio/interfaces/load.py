from base import IContextAndRequestAware
from zope.component import adapts
from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.http import IHTTPRequest, IHTTPResponse
from zope.traversing.interfaces import ITraversable


class IImportContextProvider(IContextAndRequestAware):
    
    def create_import_context():
        """Return a new `Products.GenericSetup.interfaces.IImportContext`."""
    
    def output(import_context):
        """
        Given a `Products.GenericSetup.interfaces.IImportContext` return 
        something to be sent to the user in a HTTP response. It may also
        set headers in `self.request.response` in order to prepare the output.
        """    

class IImporter(IContextAndRequestAware):
    """Export the context writing to an export context."""         
    
    def load(import_context):
        """
        Import into `self.context` reading from `import_context`, which is a 
        `Products.GenericSetup.interfaces.IImportContext`.
        """

class IImportView(IBrowserView):
    
    import_context_provider = Attribute("""An IImportContextProvider.""")  
    importer = Attribute("""An IImporter.""")
    
    def __call__():
        """
        Return: The result of importing into context with `self.importer` from 
        the import context given by `self.import_context_provider`. The actual 
        return value normally will be given by 
        `self.import_context_provider.output()`.
        """
        
class IDirectoryImportContextProvider(IImportContextProvider): pass
      
class IDictsImporter(IImporter): pass      