# test imports
from base import RatingTestCase

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingOptions

class TestOptions(RatingTestCase):

    def testInit(self):
        """
        """
        d = self.portal.document
        ro = IRatingOptions(d)
        
        self.failUnless(ro.options == {})
        self.failUnless(ro.overrides == [])
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestOptions))
    return suite
