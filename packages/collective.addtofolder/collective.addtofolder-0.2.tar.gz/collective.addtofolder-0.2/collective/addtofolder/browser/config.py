from zope.formlib import form
from zope.i18nmessageid import MessageFactory

from plone.app.controlpanel.form import ControlPanelForm

from collective.addtofolder.interfaces import IAddMenuConfiguration

_ = MessageFactory('collective.addtofolder')

class AddMenuConfigurationForm(ControlPanelForm):
    form_fields = form.Fields(IAddMenuConfiguration)
    label = _(u"Add to folder settings")
    description=_(u"")

