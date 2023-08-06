from zope.interface import Interface, Attribute
from zope.schema import Bool, Choice

class IThemeSwitcher(Interface):
    """Marker interface to implement the ThemeSwitcher View. This makes
    ThemeSwitcher local to the Plone site it is installed in. This interface
    is applied to the portal root."""
  
class ISwitchSetter(Interface):
    """The traversable object that will switch skins/themes."""
    key = Attribute("The name of the annotate key applied to the request.")
    
    def publishTraverse(request, name):
        """The method that makes the changes to the request while publishing."""

class ISkinVocabulary(Interface):
    """Skins utiltiy that will return a vocabulary of skin_name
    and interface."""
    
    def getVocab():
        """Vocabulary will be returned via this method from a list of
        sets containing (skin_name, interface)"""

class IThemeSwitcherFormSchema(Interface):
    """A schema to generate a choice (drop-down selection) of themes
    that can be switched to."""
    themeswitcher_enable = Bool(
        title=u'Enable/Disable ThemeSwitcher',
        description=u'Select if you want to enable themeswitcher.',
        required=True,
        # default=False,
        )
    themeswitcher_skin = Choice(
        title = u'Theme Selection',
        default = u'default',
        vocabulary = 'Skin Vocabulary Tool',
        description = u'Select the theme to switch to.',
        required = True
        )

