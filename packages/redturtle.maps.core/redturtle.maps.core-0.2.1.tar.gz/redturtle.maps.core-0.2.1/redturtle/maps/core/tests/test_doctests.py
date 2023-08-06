# -*- coding: utf-8 -*-
"""
@author: RedTurtle Technology
"""
#from zope.configuration.xmlconfig import XMLConfig
from Products.CMFPlone.tests import PloneTestCase
from Products.Five import fiveconfigure, zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc
from Testing.ZopeTestCase import ZopeDocTestSuite
from redturtle.maps.core import adapter

import redturtle.maps.core
import Products.Maps

from zope.testing import doctest
import unittest
@onsetup
def setup_gsxml():
    """
    setup method for test instance
    """
    
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', Products.Maps)
    zcml.load_config('configure.zcml', redturtle.maps.core)

    fiveconfigure.debug_mode = False

    ztc.installProduct('Maps')
    ztc.installPackage('redturtle.maps.core')

setup_gsxml()
ptc.setupPloneSite(extension_profiles=['redturtle.maps.core:default'])

class SPFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """
    test class
    """
    def afterSetUp(self):
        """
        operation performed after site setup in test ambient
        """
        PloneTestCase.FunctionalTestCase.afterSetUp(self)
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        self.login('manager')

def test_suite():
    """
    This sets up a test suite that actually runs the tests in the class
    above.
    """

    doc_tests = [adapter]
    suite = unittest.TestSuite()
    for test in doc_tests:
        suite.addTest(ZopeDocTestSuite(test,
                                       test_class=SPFunctionalTestCase,
                                       optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    return suite

