from zope.formlib import form
from zope.i18nmessageid import MessageFactory

from plone.app.controlpanel.form import ControlPanelForm

from slc.dublettefinder.interfaces import IDubletteFinderConfiguration

_ = MessageFactory('slc.dublettefinder')

class DubletteFinderConfigurationForm(ControlPanelForm):
    form_fields = form.Fields(IDubletteFinderConfiguration)
     
    form_name = _(u"DubletteFinder settings form")
    label = _(u"DubletteFinder settings form")
    description = _(u"Please enter the appropriate settings for the dublettefinder product")

