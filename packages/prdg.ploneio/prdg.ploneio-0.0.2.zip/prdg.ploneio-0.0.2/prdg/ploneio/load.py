import pickle

from prdg.plone.util.structure import create_obj_from_dict
from prdg.plone.util.utils import ensure_workflow_state

from Products.CMFCore.utils import getToolByName

from config import PICKLE_FILE_NAME


def publish(obj):    
    try:
        ensure_workflow_state(obj, 'published')
    except:
        wf = getToolByName(obj, 'portal_workflow')
        wf.doActionFor(obj, 'submit')
        wf.doActionFor(obj, 'publish')                        

# TODO: include parameter to choose whether to overwrite existing objects or
# not.
def load_dicts(self, import_context):    
    utool = getToolByName(self, 'portal_url')
    portal = utool.getPortalObject()
    portal_path = portal.getPhysicalPath()
    
    f = import_context.readDataFile(PICKLE_FILE_NAME)
        
    dicts = pickle.loads(f)
    for d in dicts:
        state = d.pop('workflow_dest_state', None)        
        container = portal.unrestrictedTraverse(portal_path + d['_path'][:-1])
        if d['id'] in container.objectIds():
            continue
        
        obj = create_obj_from_dict(container, d)

        if state == 'published':
            publish(obj)
        else:
            ensure_workflow_state(obj, state)        
