# -*- coding: utf-8 -*-
from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema, ATContentTypeSchema
from Products.ATContentTypes.content.base import ATCTContent
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo

from qi.jwMedia.interfaces import IMp3Audio
from qi.jwMedia.config import *
from qi.jwMedia import jwMediaMessageFactory as _
from elementtree.ElementTree import Element, SubElement, tostring



main_audioschema  = atapi.Schema((
	atapi.FileField('mp3',
		required = True,
		primary=True,
		languageIndependent = True,
		storage=atapi.AnnotationStorage(),
		widget=atapi.FileWidget(
			label=_(u"label_mp3file",default=u"Mp3 Audio file"),
		)
	),
	atapi.ImageField(
		name='image',
		required = False,
		languageIndependent = True,
		storage=atapi.AttributeStorage(),
		widget=atapi.ImageWidget(
			label=_(u"label_image",default=u"Image"),
		),
		max_size = (320,240),
		sizes={'thumbnail':(60,45)},	
	), 
	
))


mp3audio_schema = ATContentTypeSchema.copy() + main_audioschema

mp3audio_schema['title'].storage = atapi.AnnotationStorage()
mp3audio_schema['description'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(mp3audio_schema)

class Mp3Audio(ATCTContent):
	"""
	"""

	implements(IMp3Audio)
	portal_type="Mp3 Audio"
	_at_rename_after_creation = True
	schema = mp3audio_schema
	
	title = atapi.ATFieldProperty('title')
	description = atapi.ATFieldProperty('description')
	
	def recommendedXML(self):
		"""
		"""
		related_videos = [item for item in self.getRelatedItems() if item.portal_type=="Flash Video"]

		if not related_videos:
			return None

		utool = getToolByName(self, 'portal_url')
		portal_url = utool()

		recommendations = Element("recommendations")
		
		for item in related_videos:
			vrec = SubElement(recommendations,"recommendation")
			title = item.title
			title = title.decode("utf-8")
			SubElement(vrec,"title").text = title
			if item.getImage():
				SubElement(vrec,"image").text = item.absolute_url()+'/image_thumbnail'
			else:
				SubElement(vrec,"image").text = portal_url+'/++resource++qi.jwMedia.resources/video45.png'
			SubElement(vrec,"link").text = item.absolute_url()
		self.REQUEST.RESPONSE.setHeader('content-type','text/xml')
		self.REQUEST.RESPONSE.setHeader('Content-disposition','inline;filename="recommended.xml"')
		return '<?xml version="1.0" encoding="utf-8"?>'+tostring(recommendations)
	
atapi.registerType(Mp3Audio, PROJECTNAME)

