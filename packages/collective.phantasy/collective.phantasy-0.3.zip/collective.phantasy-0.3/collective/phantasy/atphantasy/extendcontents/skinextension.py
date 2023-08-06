import zope.interface
import zope.component
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import *
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content import folder

from collective.phantasy import config


class ISkinnable(zope.interface.Interface):
    """A Skinnable content item.
    """
zope.interface.classImplements(folder.ATFolder, ISkinnable)

class SkinField(ExtensionField, atapi.ReferenceField):
     """
      A schema extended field based on reference field
     """
     


class PhantasySkinSchemaExtender(object):
    zope.interface.implements(IOrderableSchemaExtender)
    zope.component.adapts(ISkinnable)
 
    _fields = [
               SkinField('local_phantasy_skin',
                   schemata='default',
                   accessor = 'getLocal_phantasy_skin',
                   multiValued=0,
                   allowed_types=(config.SKIN_PORTAL_TYPE),
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


                             
    
    




