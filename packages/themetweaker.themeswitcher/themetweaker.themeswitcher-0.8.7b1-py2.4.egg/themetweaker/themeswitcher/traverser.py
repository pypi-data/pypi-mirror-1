from zope.interface import implements, noLongerProvides, directlyProvides, directlyProvidedBy
from zope.component import adapts

from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.annotation.interfaces import IAnnotations

from themetweaker.themeswitcher.interfaces import ISwitchSetter
from themetweaker.themeswitcher.interfaces import IThemeSwitcher
from ZPublisher.BaseRequest import DefaultPublishTraverse

from zope.component import getUtilitiesFor
from plone.browserlayer.interfaces import ILocalBrowserLayerType

class SwitchSetter(object):

    adapts(IHTTPRequest)
    implements(ISwitchSetter)

    key = u'themeswitcher.marked'
    
    def __init__(self, request):
        self.request = request

    def _provide(self, iface):
        annotation = IAnnotations(self.request)
        previous = annotation.get(self.key, None)
        if previous is None:
            annotation[self.key] = iface
            return iface
        else:
            annotation[self.key] = iface
            noLongerProvides(self.request, previous)
            return previous

    def mark(self, iface):
        old = self._provide(iface)
        if not iface.providedBy(self.request):
            directlyProvides(self.request, iface)
        return self.request

class Traverser(DefaultPublishTraverse):
    """Provide traverse features
    """
    adapts(IThemeSwitcher, IHTTPRequest)
    implements(IBrowserPublisher)
    
    key = u'themeswitcher_iface'
    
    def publishTraverse(self, request, name):
        print "traversing %s and asking for %s" % (self.context, name)

        layers = [ x for x in getUtilitiesFor(ILocalBrowserLayerType) ]
        annotation = IAnnotations(self.context)
        iface = annotation.get(self.key, None)['themeswitcher_skin']
        skin_name = None
        
        # Unfortuanately we need the skin name for the changeSkin method
        # Because css and js resources require it
        for layer in layers:
            if layer[1] == iface:
                skin_name = layer[0]
                break
        if skin_name is None:
            # TODO pumazi: Can we do something meaningful here?
            self.context.changeSkin('Plone Default', request)
        elif skin_name == self.context.getCurrentSkinName():
            # If the skin is already the current one, don't do anything
            # because we have already traversed
            print "Same name? Around here we like people with the same name, pass right on through :)"
            return super(Traverser, self).publishTraverse(request, name)
        else:
            print "IThemeSwitcher!!!"
            self.context.changeSkin(skin_name, request)
            request = ISwitchSetter(request).mark(iface)

        # Then restore normal traversing
        return super(Traverser, self).publishTraverse(request, name)
        
