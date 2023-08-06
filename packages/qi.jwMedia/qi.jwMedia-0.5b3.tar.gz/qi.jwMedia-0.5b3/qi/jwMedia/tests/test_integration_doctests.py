"""This is an integration doctest test. It uses PloneTestCase and doctest
syntax.
"""

import unittest
import doctest

from zope.testing import doctestunit
from Testing import ZopeTestCase as ztc

from qi.jwMedia.tests import base

try:
	from plone.app.blob.tests import db
except:
	pass
	
def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            'tests/integration.txt', package='qi.jwMedia',
            test_class=base.jwMediaFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
            
        ])
