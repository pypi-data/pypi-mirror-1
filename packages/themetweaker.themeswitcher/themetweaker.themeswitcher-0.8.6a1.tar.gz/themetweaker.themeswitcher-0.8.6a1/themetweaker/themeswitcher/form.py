from zope.interface import implements, alsoProvides
from zope.component import adapts, getUtility, getUtilitiesFor, getMultiAdapter
from zope.i18nmessageid import MessageFactory
from plone.browserlayer.interfaces import ILocalBrowserLayerType
from Products.ATContentTypes.interface.folder import IATFolder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from themetweaker.themeswitcher.interfaces import ISkinVocabulary, IThemeSwitcherFormSchema, IThemeSwitcher
from sd.common.fields.annotation import AdapterAnnotationProperty
from sd.common.adapters.base import BaseAdapter

from plone.app.form.base import EditForm
from plone.app.form.validators import null_validator
from plone.app.form.events import EditBegunEvent, EditCancelledEvent, EditSavedEvent
import zope.event
import zope.lifecycleevent

from Products.Five.formlib.formbase import PageForm
from zope.formlib import form

_ = MessageFactory('ThemeSwitcher')

class SwitcherForm(EditForm):
    # template = ViewPageTemplateFile('editform.pt')
    form_fields = form.FormFields(IThemeSwitcherFormSchema)
    label = _(u'ThemeSwitcher Form')
    description = _(u'A form to apply a particular theme to this folder and its contents.')
    form_name = _(u'ThemeSwitcher Configuration')

    @form.action(_(u"label_save", default="Save"),
                 condition=form.haveInputWidgets,
                 name=u'save')
    def handle_save_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data, self.adapters):
            zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self.context))
            zope.event.notify(EditSavedEvent(self.context))
            # Provide the themeswitcher interface to the context
            alsoProvides(self.context, IThemeSwitcher)
            self.status = "Changes saved"
        else:
            zope.event.notify(EditCancelledEvent(self.context))
            self.status = "No changes"
            
        url = getMultiAdapter((self.context, self.request), name='absolute_url')()
        self.request.response.redirect(url)

    @form.action(_(u"label_cancel", default=u"Cancel"),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        zope.event.notify(EditCancelledEvent(self.context))
        url = getMultiAdapter((self.context, self.request), name='absolute_url')()
        self.request.response.redirect(url)
        
class ThemeSwitcherFormAdapter(BaseAdapter):
    implements(IThemeSwitcherFormSchema)
    adapts(IATFolder)

    themeswitcher_skin = AdapterAnnotationProperty(IThemeSwitcherFormSchema['themeswitcher_skin'], ns='themeswitcher_iface')

class SkinVocabulary(object):
    implements(ISkinVocabulary)
    
    @property
    def getVocab(self):
        # get the skin_names and their interfaces
        return [ x for x in getUtilitiesFor(ILocalBrowserLayerType) ]

def skinVocabularyTool(context):
    utility = getUtility(ISkinVocabulary)
    return SimpleVocabulary.fromItems(utility.getVocab)
alsoProvides(skinVocabularyTool, IVocabularyFactory)
