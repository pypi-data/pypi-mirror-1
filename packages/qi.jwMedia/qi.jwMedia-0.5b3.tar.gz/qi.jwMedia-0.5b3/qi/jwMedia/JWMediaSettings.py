from persistent import Persistent
from persistent.list import PersistentList
from persistent.dict import PersistentDict

from zope.interface import implements
from zope.component import getUtility
from zope.app.component.hooks import getSite

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot


from qi.jwMedia.interfaces import IJWMediaSettings
from qi.jwMedia import jwMediaMessageFactory as _

class JWMediaSettings(Persistent):
	"""
	"""
	
	implements(IJWMediaSettings)
	
	showLogo = True
	logoUrl = ''
	rtmpServer = ''
	rtmpStreaming = False