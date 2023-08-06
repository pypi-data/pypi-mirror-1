from zope.interface import Interface, Attribute
from zope.schema import Choice

class IThemeSwitcher(Interface):
    """Marker interface to implement the ThemeSwitcher View. This makes
    ThemeSwitcher local to the Plone site it is installed in. This interface
    is applied to the portal root."""
  
class ISwitchSetter(Interface):
    """FIXME: add a docstring """
    key = Attribute("The name of the annotate key applied to the request.")

class ISkinVocabulary(Interface):
    """Skins utiltiy that will return a vocabulary of skin_name
    and interface."""
    
    def getVocab():
        """Vocabulary will be returned via this method from a list of
        sets containing (skin_name, interface)"""

class IThemeSwitcherFormSchema(Interface):
    """A schema to generate a choice (drop-down selection) of themes
    that can be switched to."""
    themeswitcher_skin = Choice(
        title = u'ThemeSwitcher',
        default = u'default',
        vocabulary = 'Skin Vocabulary Tool',
        description = u'Theme to switch to.',
        required = True)
