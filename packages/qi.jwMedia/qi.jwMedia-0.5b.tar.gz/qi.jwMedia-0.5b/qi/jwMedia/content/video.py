# -*- coding: utf-8 -*-
from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema, ATContentTypeSchema
from Products.ATContentTypes.content.base import ATCTContent
from Products.CMFCore.utils import getToolByName
from Products.validation import V_REQUIRED

from AccessControl import ClassSecurityInfo

from qi.jwMedia.interfaces import IFlashVideo
from qi.jwMedia.config import *
from qi.jwMedia import jwMediaMessageFactory as _
from elementtree.ElementTree import Element, SubElement, tostring

StretchingVocabulary = [
	('none', _(u"None (no stretching)"),),
	('exactfit',_(u"Exact fit (disproportionate)"),),

	('uniform', _(u"Uniform (stretch with black borders)"),),
	('fill',_(u"Fill (uniform, but completely fill the display)"),),
	]

main_videoschema  = atapi.Schema((
	atapi.FileField('flv',
		required = True,
		primary = True,
		searchable = False,
		languageIndependent = True,
		storage=atapi.AnnotationStorage(migrate=True),
		validators = (('isNonEmptyFile', V_REQUIRED),
					   ('checkFileMaxSize', V_REQUIRED)),
		widget=atapi.FileWidget(
			label=_(u"label_flvfile",default=u"Flash Video file"),
		),
	),
	atapi.FileField('captions',
		required = False,
		searchable = False,
		storage=atapi.AnnotationStorage(migrate=True),
		validators = (('isNonEmptyFile', V_REQUIRED),
					   ('checkFileMaxSize', V_REQUIRED)),
		widget=atapi.FileWidget(
			label=_(u"label_captionfile",default=u"Captions XML file"),
		),
	),

	atapi.ImageField('image',
		required = False,
		searchable = False,
		languageIndependent = True,
		storage=atapi.AttributeStorage(),
		widget=atapi.ImageWidget(
			label=_(u"label_image",default=u"Image"),
		),
		max_size = (320,240),
	), 
	
),marshall = atapi.PrimaryFieldMarshaller()
)

settings_videoschema  = atapi.Schema((

	atapi.IntegerField('hsize',
		widget=atapi.IntegerWidget(
			label=_(u"label_hsize",default=u"Horizontal size"),
		),
		schemata = 'video',
		required=True,
		default=320,
		storage=atapi.AnnotationStorage()
	),

	atapi.IntegerField('vsize',
		widget=atapi.IntegerWidget(
			label=_(u"label_vsize",default=u"Vertical size"),
		),
		schemata = 'video',
		required=True,
		default=240,
		storage=atapi.AnnotationStorage()
	),

	atapi.StringField('stretching',
		widget=atapi.SelectionWidget(
			label=_(u"label_stretching",default=u"Stretching"),
		),
		schemata = 'video',
		default='uniform',
		vocabulary=StretchingVocabulary,
		enforceVocabulary = True,
		storage=atapi.AnnotationStorage()
	),

	atapi.BooleanField('allowFullscreen',
		widget=atapi.BooleanWidget(
			label=_(u"label_allowFullscreen",default=u"Allow fullscreen"),
		),
		schemata = 'video',
		default=True,
		storage=atapi.AnnotationStorage()
	),

	
))

flvideo_schema = ATContentTypeSchema.copy() + main_videoschema + settings_videoschema

flvideo_schema['title'].storage = atapi.AnnotationStorage()
flvideo_schema['description'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(flvideo_schema)

class FlashVideo(ATCTContent):
	"""
	"""

	implements(IFlashVideo)
	portal_type="Flash Video"
	_at_rename_after_creation = True
	schema = flvideo_schema
	
	title = atapi.ATFieldProperty('title')
	description = atapi.ATFieldProperty('description')
	hsize = atapi.ATFieldProperty('hsize')
	vsize = atapi.ATFieldProperty('vsize')
	overstretch = atapi.ATFieldProperty('overstretch')
	allowFullscreen = atapi.ATFieldProperty('allowFullscreen')
	
	def getFlvFilePath(self):
		try:
			return self.getFlv().getBlob()._current_filename()
		except Exception,Detail:
			return ''
	
	
atapi.registerType(FlashVideo, PROJECTNAME)

