import os
import logging
from Products.CMFPlone.utils import getToolByName
from Products.PortalTransforms.transforms.safe_html import VALID_TAGS
from Products.PortalTransforms.transforms.safe_html import NASTY_TAGS

logger = logging.getLogger('sc.kupu.objectsupport: setuphandlers')

def isNotOurProfile(context):
    return context.readDataFile("sc.kupu.objectsupport.txt") is None
    

def fixTransform(context):
    """Relax safe_html to allow object and embbed support"""
    if isNotOurProfile(context):return
    portal = context.getSite()
    valid_tags = VALID_TAGS.copy()
    nasty_tags = NASTY_TAGS.copy()
    
    tags = ['embed','object','param']
    
    for tag in tags:
        try:
            nasty_tags.pop(tag)
        except KeyError:
            pass
        valid_tags[tag] = 1
    
    kwargs = {'nasty_tags': nasty_tags,
              'valid_tags': valid_tags}
    
    transform = getattr(getToolByName(portal, 'portal_transforms'), 'safe_html')
    
    for k in list(kwargs):
        if isinstance(kwargs[k], dict):
            v = kwargs[k]
            kwargs[k+'_key'] = v.keys()
            kwargs[k+'_value'] = [str(s) for s in v.values()]
            del kwargs[k]
    
    transform.set_parameters(**kwargs)
    transform._p_changed = True
    transform.reload()
    

