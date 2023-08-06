from zope.component import getUtility
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize

from elementtree.ElementTree import Element, SubElement, tostring
from qi.jwMedia.interfaces import IJWMediaSettings

class Mp3AudioView(BrowserView):
	"""Default view of a Mp3 Audio file
	"""
	
	__call__ = ViewPageTemplateFile('mp3audio.pt')

	def logoUrl(self):
		settings = getUtility(IJWMediaSettings)
		if settings.showLogo:
			return settings.logoUrl