# -*- coding: utf-8 -*-


from zope.interface import implements
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from App.Common import rfc1123_date

from Products.CMFCore import permissions
from Products.Archetypes.public import *
from Products.ATContentTypes.content.image import ATImage
from Products.ATContentTypes.content.image import ATImageSchema
from collective.phantasy.atphantasy.interfaces import IPhantasySkinImage
from collective.phantasy.config import PROJECTNAME

PhantasySkinImageSchema = ATImageSchema.copy()
PhantasySkinImageSchema['description'].widget.visible = {'view':'invisible',
                                                         'edit':'invisible'}

class PhantasySkinImage(ATImage):
    """Phantasy Skin Image for Collective Phantasy"""

    schema = PhantasySkinImageSchema
    security = ClassSecurityInfo()
    implements(IPhantasySkinImage)
    portal_type = meta_type = 'PhantasySkinImage'
    archetype_name = 'Phantasy Skin Image'
    global_allow = False

    security.declarePrivate('initializeArchetype')
    def initializeArchetype(self, **kwargs):
        ATImage.initializeArchetype(self, **kwargs)
        # we do not want Language attributes for skinimage
        self.setLanguage('')

    security.declareProtected(permissions.View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """Make it directly viewable when entering the objects URL
        """
        duration = 20
        seconds = float(duration)*24.0*3600.0
        RESPONSE.setHeader('Expires',
                            rfc1123_date((DateTime() + duration).timeTime()))
        RESPONSE.setHeader('Cache-Control',
                           'max-age=%d' % int(seconds))
        return ATImage.index_html(self, REQUEST, RESPONSE)

registerType(PhantasySkinImage, PROJECTNAME)

