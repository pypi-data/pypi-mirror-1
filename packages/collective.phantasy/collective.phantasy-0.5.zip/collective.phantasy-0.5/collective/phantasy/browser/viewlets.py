from zope.component import getMultiAdapter
from Acquisition import aq_inner, aq_parent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common

from plone.memoize.instance import memoize

from Products.CMFPlone.utils import getToolByName, base_hasattr

from collective.phantasy.atphantasy.interfaces import IPhantasySkin


class PhantasyHeaderViewlet(common.ViewletBase):

    render = ViewPageTemplateFile('templates/phantasy-header.pt')      
    
    @memoize
    def get_cooked_css_url (self):
        """
         return cooked_css_list_urls 
         = all parents skins url
         todo : improve with zope3 technologies (>>>>> Gilles au boulot nom de dieu !!!)
        """        
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        cooked_css = []
        parent = context
        while not parent is portal :
            parent = aq_inner(parent.aq_parent)
            parent_skin = parent.restrictedTraverse('@@getPhantasySkin')
            if parent_skin() :
                pskin = aq_inner(parent_skin())
                if base_hasattr(pskin, "getCssfile"):
                     if pskin.getCssfile():
                         cooked_css.append('%s/%s' %(pskin.absolute_url(),pskin.getCssfile()))    
                cooked_css.append('%s/collective.phantasy.css' %pskin.absolute_url())            
        cooked_css.reverse()  
        return cooked_css      
        
    def getPhantasyThemeUrl(self):
        """
         todo : improve with zope3 technologies (>>>>> Gilles au boulot)
        """
        context = aq_inner(self.context)
        skin = self.getPhantasySkinObject()
        if skin :
             return '%s/collective.phantasy.css' %skin.absolute_url()
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')     
        return portal_state.portal_url()     
    
    def getPhantasySkinObject(self):
        """
          return skin object if exists
        """         
        context = aq_inner(self.context)
        skin = context.restrictedTraverse('@@getPhantasySkin')
        if skin() :
            return aq_inner(skin())  

    def update(self):
        """
         refresh cooked_css_list_urls   
         to improve
        """

        context = aq_inner(self.context)
        self.cooked_css_url = self.get_cooked_css_url()
        refresh_css=''
        skin = self.getPhantasySkinObject()
        if skin :
            if IPhantasySkin.providedBy(context) :
                # on skin object we must only see the actuel skin
                self.cooked_css_url = []
                # no cache when we are on skin object
                refresh_css = '?refresh_css=1'        
            self.cooked_css_url.append('%s/collective.phantasy.css%s' %(skin.absolute_url(),refresh_css))
            if skin.getCssfile():
                self.cooked_css_url.append('%s/%s%s' %(skin.absolute_url(),skin.getCssfile(),refresh_css))

                 

            
