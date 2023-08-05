# Zope imports
from AccessControl import Unauthorized

# zope imports
from zope.interface import directlyProvides
from zope.component import provideUtility, queryUtility

# test imports
from base import RatingTestCase

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingDefinition    
from iqpp.rating.content.definition import RatingDefinition

class TestRatingDefinition(RatingTestCase):

    def testQueryDefinition(self):
        definition = queryUtility(IRatingDefinition, "score")
        
        self.assertEqual(True, definition.isValidScore("3"))
        self.assertEqual(False, definition.isValidScore("42"))
                        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRatingDefinition))
    return suite
