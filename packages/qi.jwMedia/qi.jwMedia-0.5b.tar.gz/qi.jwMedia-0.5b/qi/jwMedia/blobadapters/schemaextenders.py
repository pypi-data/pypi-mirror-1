from zope.component import adapts
from zope.interface import implements

from plone.app.blob.field import BlobField

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from Products.ATContentTypes.content.base import ATCTContent
from Products.Archetypes import atapi
from Products.validation import V_REQUIRED

from qi.jwMedia.interfaces import IFlashVideo, IMp3Audio

from qi.jwMedia import jwMediaMessageFactory as _

class ExtensionBlobField(ExtensionField, BlobField):
	""" derivative of blobfield for extending schemas """

class BlobVideoExtender(object):
	adapts(IFlashVideo)
	implements(ISchemaExtender)

	fields = [
		ExtensionBlobField('flv',
			required = True,
			primary = True,
			default = '',
			accessor = 'getFlv',
			mutator = 'setFlv',
			languageIndependent = True,
			storage = atapi.AnnotationStorage(migrate=True),
			validators = (('isNonEmptyFile', V_REQUIRED),
						  ('checkFileMaxSize', V_REQUIRED)),
			widget=atapi.FileWidget(
				label=_(u"label_flvfile",default=u"Flash Video file"),
			)
		)
	]
	
	def __init__(self, context):
		 self.context = context

	def getFields(self):
		 return self.fields


class BlobAudioExtender(object):
	adapts(IMp3Audio)
	implements(ISchemaExtender)
	fields = [
		ExtensionBlobField('mp3',
			required = True,
			primary = True,
			default = '',
			accessor = 'getMp3',
			mutator = 'setMp3',
			languageIndependent = True,
			storage = atapi.AnnotationStorage(migrate=True),
			validators = (('isNonEmptyFile', V_REQUIRED),
						  ('checkFileMaxSize', V_REQUIRED)),
			widget=atapi.FileWidget(
				label=_(u"label_mp3file",default=u"Mp3 Audio file"),
			)
		)
	]

	def __init__(self, context):
		 self.context = context

	def getFields(self):
		 return self.fields
