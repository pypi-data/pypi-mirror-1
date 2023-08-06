from zope.component import getUtility
from zope.formlib import form

from plone.app.controlpanel.form import ControlPanelForm

from qi.jwMedia.interfaces import IJWMediaSettings
from qi.jwMedia import jwMediaMessageFactory as _


def media_settings(context):
	"""
	"""
	return getUtility(IJWMediaSettings)
	
class JWMediaSettingsControlPanel(ControlPanelForm):
	"""Control panel form view for the Newsletter settings.
	
	This uses zope.formlib to present a form from the interface above.
	"""

	form_fields = form.FormFields(IJWMediaSettings)

	form_name = _(u"Media Settings")
	label = _(u"Media settings")
	description = _(u"Please enter the appropriate settings.")
	
