# -*- coding: utf-8 -*-

"""utils views
"""



from Acquisition import aq_inner

# Zope imports
from zope.interface import implements
from Products.Five import BrowserView

# CMF/Plone imports
from Products.CMFCore.utils import getToolByName


                                                           


class PhantasyUtils(BrowserView):
    """ global utilities  """       
        
    def useJquery(self):
        """ if plone version < 3.1 return True      
        """        
        context = aq_inner(self.context)  
        pmig = getToolByName(self, 'portal_migration')
        if pmig.getFSVersionTuple() < (3, 1) :    
            return True                  
        return False
