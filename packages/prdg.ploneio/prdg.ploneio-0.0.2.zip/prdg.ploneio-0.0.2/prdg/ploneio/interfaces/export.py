from base import IContextAndRequestAware
from zope.component import adapts
from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.http import IHTTPRequest, IHTTPResponse
from zope.traversing.interfaces import ITraversable

class IExportContextProvider(IContextAndRequestAware):
    """
    Provide an export context and means to convert the result of an export
    into something that can be sent to the user in a HTTP response.
    """    

    def create_export_context():
        """Return a new `Products.GenericSetup.interfaces.IExportContext`."""    
    
    def output(export_context):
        """
        Given a `Products.GenericSetup.interfaces.IExportContext` return 
        something to be sent to the user in a HTTP response. It may also
        set headers in `self.request.response` in order to prepare the output.
        """
    
class IExporter(IContextAndRequestAware):
    """Export the context writing to an export context."""         
    
    def export(export_context):
        """
        Export `self.context` writing to `export_context`, which is a 
        `Products.GenericSetup.interfaces.IExportContext`.
        """
        
class IExportView(IBrowserView):
    
    export_context_provider = Attribute("""An IExportContextProvider.""")  
    exporter = Attribute("""An IExporter.""")
    
    def __call__():
        """
        Return: The result of exporting the context with `self.exporter` to the
        export context given by `self.export_context_provider`. The actual 
        return value normally will be given by 
        `self.export_context_provider.output()`.
        """

# TODO: document the following interfaces.    

class IArchiveExportContextProvider(IExportContextProvider): pass
class IDirectoryExportContextProvider(IExportContextProvider): pass
class IStringExportContextProvider(IExportContextProvider): pass

class IDictsExporter(IExporter): pass
class IHTMLExporter(IExporter): pass
class IDictsReprExporter(IExporter): pass

