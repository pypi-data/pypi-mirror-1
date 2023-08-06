import unittest
from collective.inplacetopicview.tests import base

from Products.CMFCore.utils import getToolByName

class TestSetup(base.TestCase):
    """Test if classic cms is well setup"""

    def test_types(self):
        typestool = self.portal.portal_types

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
