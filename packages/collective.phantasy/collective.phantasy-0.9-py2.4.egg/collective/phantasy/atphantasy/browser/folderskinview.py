# -*- coding: utf-8 -*-



# Zope imports
import zope.component
from zope.interface import implements
from Acquisition import aq_inner
from zope.component import getMultiAdapter

# Plone, Five imports
from Products.CMFPlone.utils import getToolByName, base_hasattr
from Products.Five import BrowserView
# Product imports
from interfaces import IFolderSkinView
from collective.phantasy.atphantasy.interfaces import IPhantasySkin
from collective.phantasy import config


class FolderSkinView(BrowserView):
    """ utils to get skin in folder_contents"""

    implements(IFolderSkinView)       
    
    def getPhantasySkin (self):
        """
        return the referenced phantasy_skin if exists (ATFolder only for now) or 
        the last modified skin object in folder_contents (for the site) or the context
        when context = skin onject
        """
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        
        #return skin for preview when we are in skin object
        if IPhantasySkin.providedBy(context) :
            return context            
            
        # otherwise return the last modified skin in portal
        elif context is portal :    
            crit = {}
            path = {}
            path['query'] = '/'.join(context.getPhysicalPath())
            path['depth'] = 1
            crit['path'] = path
            crit['object_provides'] = 'collective.phantasy.atphantasy.interfaces.skin.IPhantasySkin' 
            crit['sort_on']= 'modified'
            crit['sort_order'] = 'reverse'
            crit['sort_limit'] = 1
            ct = getToolByName(context, 'portal_catalog')
            results = ct.searchResults(**crit)[:1]
            if results :
                return results[0].getObject()            

        # only ATFolder have 'phantasy_skin' property (see extendcontents )
        # but is there an error in schemaextender ? impossible to get context.getField_name()
        # when accessor getField_name exits. So we made another strange thing
        elif base_hasattr(context, 'Schema') :
            schema = context.Schema() or {}
            if schema.has_key ('local_phantasy_skin'):
                f = schema['local_phantasy_skin']
                accessor =  f.getAccessor(context)
                return accessor() or None    

                          
        

