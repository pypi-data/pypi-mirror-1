import zope.interface
import zope.component
from zope.app.component.hooks import getSite
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import *
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content import folder




class ISkinnable(zope.interface.Interface):
    """A Skinnable content item.
    """
zope.interface.classImplements(folder.ATFolder, ISkinnable)

class SkinField(ExtensionField, atapi.ReferenceField):
    """
      A schema extended field based on reference field
    """        
    def getPhantasySkinType(self) :
        """Phantasy Skin Type depend on portal_properties"""
        portal = getSite()        
        stp = getToolByName(portal, 'portal_properties').site_properties
        return (stp.getProperty('phantasy_skin_portal_type', 'PhantasySkin').strip('\n'),)     
        
    allowed_types = property(fget = getPhantasySkinType) 
              
  
  

class PhantasySkinSchemaExtender(object):
    zope.interface.implements(IOrderableSchemaExtender)
    zope.component.adapts(ISkinnable)
      
 
    _fields = [
               SkinField('local_phantasy_skin',
                   schemata='default',
                   accessor = 'getLocal_phantasy_skin',
                   multiValued=0,
                   relationship='Rel1',
                   widget=ReferenceBrowserWidget(
                        label = 'Phantasy Skin',
                        description='Browse for a skin.')
               ),
             ]                          
                      
             
    def __init__(self, context):
        self.context = context
    
    def getFields(self):
        return self._fields
    
    def getOrder(self, original):
        defschemata = original['default']
        idx = defschemata.index('title')
        defschemata.remove('local_phantasy_skin')
        defschemata.insert(idx+1, 'local_phantasy_skin')
        return original     



                                 
    
    




