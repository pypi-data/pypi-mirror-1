import pickle
from logging import getLogger

from zope.component import getUtility

from Products.Five.browser import BrowserView
from Products.GenericSetup.context import DirectoryImportContext
from Products.CMFCore.utils import getToolByName

from prdg.plone.util.structure import create_dict_for_all_objs

from prdg.ploneio.config import DIRECTORY_ARG, PICKLE_FILE_NAME
from prdg.ploneio.load import load_dicts

# TODO: create automatic tests.

def publish(obj):    
    try:
        ensure_workflow_state(obj, 'published')
    except:
        wf = getToolByName(obj, 'portal_workflow')
        wf.doActionFor(obj, 'submit')
        wf.doActionFor(obj, 'publish')

class LoadView(BrowserView):
    """Export the context workflow to CSV as a one-off
    """
    
    log = getLogger(__name__)
    
    def get_import_context(self):
        """Return: a new `Products.GenericSetup.interfaces.IImportContext`."""        
    
    def load(self, import_context):
        """Import reading from `import_context`."""
    
    def output(self, import_context):
        """Return: something to be returned by `__call__()`."""
        return 'Success.'
    
    def __call__(self):
        import_context = self.get_import_context()
        self.load(import_context)
        return self.output(import_context)
                    
class FromDirectoryLoadView(LoadView):
    
    def get_import_context(self):
        return DirectoryImportContext(
            None, 
            self.request[DIRECTORY_ARG], 
            encoding='utf8'
        )    
        
class DictsLoadView(LoadView):    
    load = load_dicts
                
class DictsFromDirectoryLoadView(FromDirectoryLoadView, DictsLoadView):
    get_import_context = FromDirectoryLoadView.get_import_context                
    
    
    def load(self, import_context):
        load_dicts(self.context, import_context)
    