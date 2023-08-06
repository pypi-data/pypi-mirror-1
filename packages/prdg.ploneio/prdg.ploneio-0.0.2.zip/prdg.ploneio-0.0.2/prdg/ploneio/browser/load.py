from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.GenericSetup.context import DirectoryImportContext
from base import ContextAndRequestAware
from prdg.ploneio.config import DIRECTORY_ARG
from prdg.ploneio.interfaces.load import (IImportView, 
    IDirectoryImportContextProvider, IDictsImporter)
from prdg.ploneio.load import load_dicts
from zope.component import getMultiAdapter, getUtility
from zope.interface import implements

# TODO: create automatic tests.

def publish(obj):    
    try:
        ensure_workflow_state(obj, 'published')
    except:
        wf = getToolByName(obj, 'portal_workflow')
        wf.doActionFor(obj, 'submit')
        wf.doActionFor(obj, 'publish')
                    
class DirectoryImportContextProvider(ContextAndRequestAware):
    implements(IDirectoryImportContextProvider)
    
    def create_import_context(self):
        return DirectoryImportContext(
            None, 
            self.request[DIRECTORY_ARG], 
            encoding='utf8'
        )
    def output(self, import_context):
        return 'Success.'
        
class DictsImporter(ContextAndRequestAware):
    implements(IDictsImporter)
    
    def load(self, import_context):
        load_dicts(self.context, import_context)
        
class BaseImportView(BrowserView):
    implements(IImportView)

    import_context_provider_interface = None
    importer_interface = None
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.import_context_provider = getMultiAdapter(
            (context, request), 
            self.import_context_provider_interface
        )
        self.importer = getMultiAdapter(
            (context, request), 
            self.importer_interface
        )
    
    def __call__(self):
        import_context = self.import_context_provider.create_import_context()
        self.importer.load(import_context)
        return self.import_context_provider.output(import_context)        
                
class DictsFromDirectoryImportView(BaseImportView):
    import_context_provider_interface = IDirectoryImportContextProvider
    importer_interface = IDictsImporter