# fix reference browser bugs
# TODO : use a new widget based on collective.plonefinder
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.Archetypes.Registry import registerWidget

class PhantasyBrowserWidget(ReferenceBrowserWidget):
    _properties = ReferenceBrowserWidget._properties.copy()
    _properties.update({
        'helper_js': ('referencebrowser.js', '++resource++collective.phantasy.javascripts/phantasy_browser.js'),
        })

registerWidget(PhantasyBrowserWidget,
               title='Reference Browser',
               description=('Reference widget that allows you to browse or search the portal for phantasy skins to refer to.'),
               used_for=('Products.Archetypes.Field.ReferenceField',)
               )