import unittest
from rc.policy.tests.base import RcPolicyTestCase

from Products.CMFCore.utils import getToolByName

class TestSetup(RcPolicyTestCase):

    def test_portal_title(self):
        self.assertEquals("Redaktionskomponente des SFB 600", self.portal.getProperty('title'))

    def test_portal_description(self):
        self.assertEquals("Evaluationsumgebung", self.portal.getProperty('description'))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
