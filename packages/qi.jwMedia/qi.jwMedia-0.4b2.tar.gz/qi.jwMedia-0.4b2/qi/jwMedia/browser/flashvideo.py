from urllib import urlencode
from zope.component import getUtility
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize

from elementtree.ElementTree import Element, SubElement, tostring
from qi.jwMedia.interfaces import IJWMediaSettings
import base64

class FlashVideoView(BrowserView):
	"""Default view of a FlashVideo
	"""
	
	__call__ = ViewPageTemplateFile('flashvideo.pt')
	
	def __init__(self, context, request):
		BrowserView.__init__(self, context, request)
		self.mediasettings = getUtility(IJWMediaSettings)
	
	def logoUrl(self):
		if self.mediasettings.showLogo:
			return self.mediasettings.logoUrl
	
	def mediaType(self):
		if self.mediasettings.rtmpStreaming:
			return 'rtmp'
		else:
			return 'video'

	def fileUrl(self):
		context = aq_inner(self.context)
		if self.mediasettings.rtmpStreaming:
			url = 'rtmp://'+self.mediasettings.rtmpServer+'/'
			#fpath = urlencode({'id':context.getFlvFilePath()})		
			fpath = base64.b64encode(context.getFlvFilePath())
			url = url + fpath
			return url
		else:
			return context.absolute_url()+"/getFlv"
		
	def captionsUrl(self):
		context = aq_inner(self.context)
		if len(context.getCaptions()):
			return context.absolute_url()+"/getCaptions"
		return ""
		
	def rtmpUrl(self):
		if not self.mediasettings.rtmpStreaming:
			return ''
		url = 'rtmp://'+self.mediasettings.rtmpServer+'/?'
		#return url
		context = aq_inner(self.context)
		fpath=''
		fpath = urlencode({'id':context.getFlvFilePath()})
		
		url = url + fpath
		return url
		#url = 'rtmp://'