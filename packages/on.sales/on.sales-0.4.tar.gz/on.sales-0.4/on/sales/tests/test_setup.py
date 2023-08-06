import unittest
from Products.CMFCore.utils import getToolByName

from on.sales.tests.base import SalesTestCase

class TestSetup(SalesTestCase):
    def test_add_permission_for_salesagents(self):
        self.failUnless('on: Add SalesAgent' in [r['name'] for r in 
                                self.portal.permissionsOfRole('Manager') if r['selected']]
				)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
