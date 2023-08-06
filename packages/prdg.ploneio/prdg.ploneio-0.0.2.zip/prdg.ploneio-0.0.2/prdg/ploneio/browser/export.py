from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.GenericSetup.context import (TarballExportContext, 
    DirectoryExportContext)
from base import ContextAndRequestAware
from prdg.plone.util.structure import create_dict_for_all_objs
from prdg.ploneio.config import HTML_TEMPLATE, DIRECTORY_ARG
from prdg.ploneio.context import StringExportContext
from prdg.ploneio.export import export_dicts, export_dicts_repr
from prdg.ploneio.interfaces.export import (IExportView, 
    IArchiveExportContextProvider, IDirectoryExportContextProvider, IDictsExporter, 
    IHTMLExporter, IDictsReprExporter, IStringExportContextProvider, 
    IContextAndRequestAware)
from zope.component import getMultiAdapter
from zope.interface import implements

# TODO: create automatic tests.

class ArchiveExportContextProvider(ContextAndRequestAware):
    implements(IArchiveExportContextProvider)
    
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
                
class DirectoryExportContextProvider(ContextAndRequestAware):
    implements(IDirectoryExportContextProvider)    
    
    def create_export_context(self):
        export_context = DirectoryExportContext(
            None, 
            self.request[DIRECTORY_ARG], 
            encoding='utf8'
        )
        return export_context
    
    def output(self, export_context):
        return 'Success.' 

class StringExportContextProvider(ContextAndRequestAware):
    implements(IStringExportContextProvider)    
        
    def create_export_context(self):
        return StringExportContext()        
    
    def output(self, export_context):
        return export_context.getString()
    
class DictsExporter(ContextAndRequestAware):
    implements(IDictsExporter)    
    
    def export(self, export_context):        
        return export_dicts(self.context, export_context)    
        
class HTMLExporter(ContextAndRequestAware):
    implements(IHTMLExporter)
    
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
                export_context.writeDataFile(
                    filename, 
                    html, 
                    'text/xhtml', 
                    directory
                ) 

class DictsReprExporter(ContextAndRequestAware):
    implements(IDictsReprExporter)
    
    def export(self, export_context):
        return export_dicts_repr(self.context, export_context)
    
class BaseExportView(BrowserView):
    implements(IExportView)

    export_context_provider_interface = None
    exporter_interface = None
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.export_context_provider = getMultiAdapter(
            (context, request), 
            self.export_context_provider_interface
        )
        self.exporter = getMultiAdapter(
            (context, request), 
            self.exporter_interface
        )        
        
    def __call__(self):
        export_context = self.export_context_provider.create_export_context()        
        self.exporter.export(export_context)
        return self.export_context_provider.output(export_context)
        
class DictsToArchiveExportView(BaseExportView):
    export_context_provider_interface = IArchiveExportContextProvider
    exporter_interface = IDictsExporter    
        
class DictsToDirectoryExportView(BaseExportView):
    export_context_provider_interface = IDirectoryExportContextProvider
    exporter_interface = IDictsExporter  
                
class HTMLToArchiveExportView(BaseExportView):
    export_context_provider_interface = IArchiveExportContextProvider
    exporter_interface = IHTMLExporter        
        
class HTMLToDirectoryExportView(BaseExportView):
    export_context_provider_interface = IDirectoryExportContextProvider
    exporter_interface = IHTMLExporter    
    
class DictsReprToStringExportView(BaseExportView):
    export_context_provider_interface = IStringExportContextProvider
    exporter_interface = IDictsReprExporter 

