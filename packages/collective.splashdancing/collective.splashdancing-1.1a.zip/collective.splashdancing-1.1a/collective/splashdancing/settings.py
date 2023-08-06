from persistent.dict import PersistentDict
from zope import interface
from zope import component
from zope.annotation.interfaces import IAnnotations
from plone.z3cform import z2
from plone.z3cform.widget import singlecheckboxwidget_factory
import z3c.form

from collective.dancing import channel
from collective.dancing import browser

from interfaces import IHTMLClassIDStripper
from collective.splashdancing import splashdancingMessageFactory as _

class HTMLClassIDStripperForm(z3c.form.form.EditForm):

    @property
    def fields(self):
        fields = z3c.form.field.Fields(IHTMLClassIDStripper)
#         fields['enabled'].widgetFactory[z3c.form.interfaces.INPUT_MODE] = (
#            singlecheckboxwidget_factory)
        return fields
    
    def getContent(self):
        return dict(IHTMLClassIDStripper(self.context))

    @z3c.form.button.buttonAndHandler(_('Save'), name='save')
    def handle_save(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = z3c.form.form.EditForm.formErrorsMessage
            return
        IHTMLClassIDStripper(self.context).update(data)
        self.status = z3c.form.form.EditForm.successMessage
        self.context._p_changed = True
        

class HTMLClassIDStripperView(browser.channel.ChannelAdministrationView):

    label = _("HTML Class ID Stripper setup")
    def contents(self):
        # A call to 'switch_on' is required before we can render z3c.forms.
        z2.switch_on(self)
        return HTMLClassIDStripperForm(self.context, self.request)()

defaults = {'enabled':True,
            'stripping_rules':'class|discreet',
            }

@interface.implementer(IHTMLClassIDStripper)
@component.adapter(channel.IPortalNewsletters)
def html_id_class_stripper(context):
    annotations = IAnnotations(context)
    if not annotations.has_key('collective.splashdancing'):
        annotations['collective.splashdancing'] = PersistentDict(defaults)
    return annotations['collective.splashdancing']
