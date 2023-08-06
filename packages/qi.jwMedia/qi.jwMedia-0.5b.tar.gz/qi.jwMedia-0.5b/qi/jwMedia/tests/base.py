"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of Plone's
products are loaded, and a Plone site will be created. This happens at module
level, which makes it faster to run each test, but slows down test runner
startup.
"""

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Five.testbrowser import Browser

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from kss.core.BeautifulSoup import BeautifulSoup

from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
	"""Set up the package and its dependencies.
	
	The @onsetup decorator causes the execution of this body to be deferred
	until the setup of the Plone site testing layer. We could have created our
	own layer, but this is the easiest way for Plone integration tests.
	"""	   
	
	fiveconfigure.debug_mode = True
	import qi.jwMedia.tests
	zcml.load_config('configure.zcml', qi.jwMedia)
	fiveconfigure.debug_mode = False
	
	
	ztc.installPackage('qi.jwMedia')
	

setup_product()
ptc.setupPloneSite(products=['qi.jwMedia'])

class jwMediaTestCase(ptc.PloneTestCase):
	"""We use this base class for all the tests in this package. If necessary,
	we can put common utility or setup code in here. This applies to unit 
	test cases.
	"""

class jwMediaFunctionalTestCase(ptc.FunctionalTestCase):
	"""We use this class for functional integration tests that use doctest
	syntax. Again, we can put basic common utility or setup code in here.
	"""
	BeautifulSoup = BeautifulSoup
	
	def getCredentials(self):
		return '%s:%s' % (ptc.default_user,
			ptc.default_password)

	def getBrowser(self, loggedIn=True):
		""" instantiate and return a testbrowser for convenience """
		browser = Browser()
		if loggedIn:
			auth = 'Basic %s' % self.getCredentials()
			browser.addHeader('Authorization', auth)
		return browser

