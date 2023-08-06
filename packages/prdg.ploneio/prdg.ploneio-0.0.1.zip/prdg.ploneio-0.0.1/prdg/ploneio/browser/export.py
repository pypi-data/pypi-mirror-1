import pickle
from logging import getLogger

from zope.component import getUtility

from Products.Five.browser import BrowserView
from Products.GenericSetup.context import (TarballExportContext, 
    DirectoryExportContext)
from Products.CMFCore.utils import getToolByName

from prdg.ploneio.config import (HTML_TEMPLATE, DIRECTORY_ARG)
from prdg.ploneio.context import StringExportContext
from prdg.ploneio.export import (export_dicts, export_dicts_repr)
from prdg.plone.util.structure import create_dict_for_all_objs

# TODO: create automatic tests.

class ExportView(BrowserView):
    """Export the context workflow to CSV as a one-off
    """
    
    log = getLogger(__name__)
    
    def create_export_context(self):
        """Return: a new `Products.GenericSetup.interfaces.IExportContext`."""        
    
    def export(self, export_context):
        """Export `wiriting to `export_context`."""
    
    def output(self, export_context):
        """Return: something to be returned by `__call__()`."""
        return 'Success.'
    
    def __call__(self):
        export_context = self.create_export_context()
        self.export(export_context)
        return self.output(export_context)

class ToArchiveExportView(ExportView):
    
    def create_export_context(self):
        export_context = TarballExportContext(None, 'utf8')
        export_context._archive_filename = self.context.getId() + '.tar.gz'
        return export_context
        
    def output(self, export_context):
        self.request.response.setHeader("Content-type", "application/x-gzip")
        self.request.response.setHeader(
            "Content-disposition",
            "attachment;filename=%s" % export_context.getArchiveFilename()
        )    
        return export_context.getArchive()        
                
class ToDirectoryExportView(ExportView):
    
    def create_export_context(self):
        export_context = DirectoryExportContext(
            None, 
            self.request[DIRECTORY_ARG], 
            encoding='utf8'
        )
        return export_context     
        
class ToStringExportView(ExportView):
    
    def create_export_context(self):
        return StringExportContext()        
    
    def output(self, export_context):
        return export_context.getString()
    
class DictsExportView(ExportView):
    
    def export(self, export_context):        
        return export_dicts(self.context, export_context)    
        
class HTMLExportView(ExportView):
    
    def export(self, export_context):        
        utool = getToolByName(self.context, 'portal_url')
        portal = utool.getPortalObject()
        
        root_obj_to_dump = self.context
        query = {'path': '/'.join(root_obj_to_dump.getPhysicalPath())}    
        for d in create_dict_for_all_objs(portal, query):
            body_html = d.get('body', d.get('text', None))
            if body_html:
                filename = d['id'] + '.html'
                directory = '/'.join(d['_path'])
                            
                html = HTML_TEMPLATE % (d['title'], body_html)
                self.log.info('Creating %s ...' % filename)
                export_context.writeDataFile(
                    filename, 
                    html, 
                    'text/xhtml', 
                    directory
                ) 

class DictsReprExportView(ExportView):
    
    def export(self, export_context):
        return export_dicts_repr(self.context, export_context)        

class DictsToArchiveExportView(ToArchiveExportView, DictsExportView):
    create_export_context = ToArchiveExportView.create_export_context                
    output = ToArchiveExportView.output
    export = DictsExportView.export    
        
class DictsToDirectoryExportView(ToDirectoryExportView, DictsExportView):
    create_export_context = ToDirectoryExportView.create_export_context                
    output = ToDirectoryExportView.output
    export = DictsExportView.export
        
        
class HTMLToArchiveExportView(ToArchiveExportView, HTMLExportView):
    create_export_context = ToArchiveExportView.create_export_context                
    output = ToArchiveExportView.output
    export = HTMLExportView.export        
        
class HTMLToDirectoryExportView(ToDirectoryExportView, HTMLExportView):
    create_export_context = ToDirectoryExportView.create_export_context                
    output = ToDirectoryExportView.output
    export = HTMLExportView.export    
    
class DictsReprToStringExportView(ToStringExportView, DictsReprExportView):
    create_export_context = ToStringExportView.create_export_context                
    output = ToStringExportView.output
    export = DictsReprExportView.export       
              