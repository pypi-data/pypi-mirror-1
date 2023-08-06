from zope.interface import directlyProvidedBy, directlyProvides, noLongerProvides
from zope.component import getUtilitiesFor
from plone.browserlayer.interfaces import ILocalBrowserLayerType
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

def markLayer(site, event):
    """Mark the request with all installed layers. A replacement for
    plone.browserlayer.layer.mark_layer
    """
    request = event.request
    # This will need changed to all browserlayers that are not skins.
    # Formerly done by registering the theme's interface with IBrowserSkinType.
    skin_browser_layers = []
    non_skin_browser_layers = []
    preferred_skin = getToolByName(getSite(), 'portal_skins').get('default_skin')
    
    # browser_layers data structure: [(name, interface), ...]
    browser_layers = [ x for x in getUtilitiesFor(ILocalBrowserLayerType) ]
    skins = set(getToolByName(getSite(), 'portal_skins').getSkinSelections())
    for layer in browser_layers:
        if layer[0] in skins:
            skin_browser_layers.append(layer)
            if layer[0] == preferred_skin:
                directlyProvides(request, layer[1])
        else:
            non_skin_browser_layers.append(layer)
    if len(non_skin_browser_layers) != 0:
        directlyProvides(request, *non_skin_browser_layers)
    
    # +++++++++++++++++++++++++++++++++++++++++++++++++++
    # THE OLD CODE (here for quick reference)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++
    # layers = getAllUtilitiesRegisteredFor(ILocalBrowserLayerType)
    # ifaces = list(layers) + list(directlyProvidedBy(request))
    #     
    # # Since we allow multiple markers here, we can't use 
    # # zope.publisher.browser.applySkin() since this filters out 
    # # IBrowserSkinType interfaces, nor can we use alsoProvides(), since
    # # this appends the interface (in which case we end up *after* the
    # # default Plone/CMF skin)
    # 
    # directlyProvides(request, *ifaces)

