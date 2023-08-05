# Copyright 2007, Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 
#
__author__ = """Jens Klein <jens@bluedynamics.com>"""

from zope.interface import implements
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.interfaces import INonStructuralFolder
from interfaces import IPostitFetcher

class PostitFromContainerFetcher(object):
    """fetches postits from current container"""
    
    implements(IPostitFetcher)
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self):
        res = []
        cat = getToolByName(self.context, 'portal_catalog')     
        context = aq_inner(self.context)
        while True:            
            if IFolderish.providedBy(context) and \
               not INonStructuralFolder.providedBy(context):
                break
            if getattr(context, 'isPrincipiaFolderish', False) and \
               not INonStructuralFolder.providedBy(context):
                break
            context = aq_parent(context)
        query = {}
        query['portal_type'] = 'PostIt'
        query['path'] = {'query': '/'.join(context.getPhysicalPath()), 
                         'depth': -1,}           
        query['sort_on'] = 'getObjPositionInParent'
        brains = cat(**query)
        for brain in brains:
            part = dict()
            part['creator'] = brain.Creator
            part['text'] = brain.getPostit
            res.append(part)
        return  res

    