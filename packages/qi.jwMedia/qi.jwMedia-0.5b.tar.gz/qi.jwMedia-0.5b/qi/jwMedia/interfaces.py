from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from qi.jwMedia import jwMediaMessageFactory as _

class IFlashVideo(Interface):
	"""
	"""

class IMp3Audio(Interface):
	"""
	"""

		
class IJWMediaSettings(Interface):
	"""
	"""
	showLogo = schema.Bool(title=_(u"label_showLogo",default=u"Show logo watermark on videos"),
		description=_(u"help_showLogo",default=u"Whether a watermark should be shown when a video is played."),)
	logoUrl = schema.TextLine(title=_(u"label_logoUrl",default=u"Logo url"),
		description=_(u"help_logoUrl",default=u"The url where the logo is found."),
		required = False)
	rtmpServer = schema.ASCIILine(title=_(u"label_rtmpserver", default=u"RTMP Server"),
		description=_(u"help_rtmpserver",default=u"Please enter the RTMP server domain name"),
		required = False)
	rtmpStreaming = schema.Bool(title=_(u"label_rtmpstreaming",default=u"Use rtmp streaming"),
		description=_(u"help_rtmpstreaming",default=u"Whether content will be served through an rtmp server."),)
	