#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################


"""
Test ZCML directives
"""

import os
import unittest

import zope.component
from zope.configuration import xmlconfig
from zope.component.testing import PlacelessSetup

class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(DirectivesTest, self).setUp()
        os.environ['TESTING'] = '1'
        gsm = zope.component.getGlobalSiteManager()
        here = os.path.dirname(__file__)
        zcml = file(os.path.join(here, "example.zcml")).read()
        self.context = xmlconfig.string(zcml)
        super(DirectivesTest, self).tearDown()

    def tearDown(self):
        super(DirectivesTest, self).tearDown()
        del os.environ['TESTING']

    def testSimple(self):
        pass

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
