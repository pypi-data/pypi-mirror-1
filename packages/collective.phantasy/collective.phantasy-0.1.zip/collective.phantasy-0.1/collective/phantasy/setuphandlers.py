import transaction
from Products.CMFCore.utils import getToolByName
from collective.phantasy import config

PRODUCT_DEPENDENCIES= ('SmartColorWidget', 'plone.browserlayer')

def setupVarious(context):

    if context.readDataFile('collective.phantasy_various.txt') is None:
        return

    site = context.getSite()
    install_dependencies(site)
    if config.INSTALL_PHANTASY_CONTENTS :
        install_atphantasy_contents(site)
        transaction.savepoint()


def install_dependencies(context):

    pq = getToolByName(context, 'portal_quickinstaller')
    for product in PRODUCT_DEPENDENCIES :
        if pq.isProductInstalled(product):
            pq.reinstallProducts([product])
            transaction.savepoint()
        else :
            pq.installProduct(product)
            transaction.savepoint()    

def install_atphantasy_contents(context):
    """install atphantasy skin structure"""
    portal = getToolByName(context, 'portal_url').getPortalObject()
    skinroot = {
                "type_name" : "PhantasySkin",
                "id" : "phantasy-root-skin",
                "title" : "Phantasy Root Skin",
               }
    skinroot_data = { 
                "portalWidth" : "1000px",
                "portalHorizontalPosition" : "0 auto 0 auto",
                "backgroundColor" : "#f6e9e9",
                "portalBackgroundColor" : "#ffffff",
                "evenRowBackgroundColor" : "#f6e9e9",
                "globalBackgroundColor" : "#f6e9e9",
                "globalFontColor" : "#7d3939",
                "globalBorderColor" : "#d8d8d8",
                "contentViewBackgroundColor" : "#f1d8d4",
                "contentViewFontColor" : "#820707",
                "contentViewBorderColor" : "#820707",
                "Language": "",
                }
    skinrepository = {"type_name" : "PhantasySkinsRepository",
                      "id" : "phantasy-skins-repository",
                      "title" : "Phantasy Skins Repository",
                      "Language": "",
                     }     
    foldersample = {"type_name" : "Folder",
                    "id" : "folder-with-other-skin",
                    "title" : "Folder With Other Skin",
                   }                        
    skinsample = {
                  "type_name" : "PhantasySkin",
                  "id" : "phantasy-sample-skin",
                  "title" : "Phantasy Sample Skin",
                 }
    skinsample_data = {                  
                  "portalWidth" : "1000px",
                  "portalHorizontalPosition" : "0 auto 0 auto",
                  "backgroundColor" : "#e8deec",
                  "portalBackgroundColor" : "#ffffff",
                  "evenRowBackgroundColor" : "#e8deec",
                  "globalBackgroundColor" : "#e8deec",
                  "globalFontColor" : "#7d3939",
                  "globalBorderColor" : "#d8d8d8",
                  "contentViewBackgroundColor" : "#f1d8d4",
                  "contentViewFontColor" : "#820707",
                  "contentViewBorderColor" : "#820707",
                  "Language": "",
                  }                    
    if 'phantasy-root-skin' not in portal.objectIds() :
        portal.invokeFactory( **skinroot)
        o = getattr(portal, 'phantasy-root-skin')
        o.edit(**skinroot_data)
    if 'phantasy-skins-repository' not in portal.objectIds() :
        portal.invokeFactory( **skinrepository)        
        o = getattr(portal, 'phantasy-skins-repository')
        o.invokeFactory( **skinsample)
        skin = getattr(o, 'phantasy-sample-skin')
        skin.edit(**skinsample_data)
        skinuid = skin.UID()
        if 'folder-with-other-skin' not in portal.objectIds() :
            portal.invokeFactory( **foldersample)   
            o = getattr(portal, 'folder-with-other-skin') 
            o.edit(local_phantasy_skin= skinuid)
            
    # disallow skins types at root after installation
    ttool = getToolByName(context, 'portal_types')
    types = ['PhantasySkin', 'PhantasySkinsRepository']
    for type in types :
        fti = getattr(ttool, type, None)
        if fti :
            fti._setPropValue('global_allow', 0)        
            
