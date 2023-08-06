from zope.formlib import form
from zope.i18nmessageid import MessageFactory

from plone.app.controlpanel.form import ControlPanelForm

from slc.mindmap.interfaces import IMindMeisterConfiguration

_ = MessageFactory('slc.mindmeister')

class MindMeisterConfigurationForm(ControlPanelForm):
    form_fields = form.Fields(IMindMeisterConfiguration)
     
    form_name = _(u"MindMeister API settings form")
    label = _(u"MindMeister API settings form")
    description = _(u"Please enter the appropriate settings for the slc.mindmeister product")


