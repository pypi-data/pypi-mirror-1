import unittest
from zope.component import getUtility

from collective.ATClamAV.interfaces import IAVScanner
from collective.ATClamAV.tests.base import ATClamAVTestCase

class TestScanner(ATClamAVTestCase):
    """
    """
    def afterSetUp(self):
        self.scanner = getUtility(IAVScanner)
        
    def test_ping(self):
        """
        """
        self.assertEquals(self.scanner.ping(),True)

    def test_scanBuffer(self):
        """
        """
        # Try a virus...
        self.assertEquals(self.scanner.scanBuffer(self.EICAR),'Eicar-Test-Signature FOUND')
        # And a normal file...
        self.assertEquals(self.scanner.scanBuffer('This is not a virus'),None)
        
        
def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestScanner))
    return suite