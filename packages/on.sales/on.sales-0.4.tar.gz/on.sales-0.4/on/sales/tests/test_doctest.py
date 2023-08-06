import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from on.sales.tests import base

def test_suite():
    #import pdb; pdb.set_trace()
    return unittest.TestSuite([

        # Unit tests
        ztc.ZopeDocFileSuite(
            'README.txt', package='on.sales',
            test_class=base.SalesFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
        
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
	
