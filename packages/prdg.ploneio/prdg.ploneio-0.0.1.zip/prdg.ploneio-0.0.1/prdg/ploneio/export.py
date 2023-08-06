from Products.CMFCore.utils import getToolByName

from prdg.plone.util.structure import create_dict_for_all_objs

from config import PICKLE_FILE_NAME, PICKLE_MIME_TYPE, DICT_REPR_FILE_NAME

from StringIO import StringIO
from pprint import pprint
import pickle

def create_dict_for_all_objs_in_context(self):
    utool = getToolByName(self, 'portal_url')
    portal = utool.getPortalObject()
    
    query = {'path': '/'.join(self.getPhysicalPath())}    
    
    for d in create_dict_for_all_objs(portal, query):
        yield d        

def export_dicts(self, export_context):
    objs = list(create_dict_for_all_objs_in_context(self))        
    dump = pickle.dumps(objs)    
    export_context.writeDataFile(PICKLE_FILE_NAME, dump, PICKLE_MIME_TYPE)
    
def export_dicts_repr(self, export_context):
    objs = list(create_dict_for_all_objs_in_context(self))
    out = StringIO()
    text = pprint(objs, stream=out)

    export_context.writeDataFile(
        DICT_REPR_FILE_NAME, 
        out.getvalue(), 
        'text/plain'
    )