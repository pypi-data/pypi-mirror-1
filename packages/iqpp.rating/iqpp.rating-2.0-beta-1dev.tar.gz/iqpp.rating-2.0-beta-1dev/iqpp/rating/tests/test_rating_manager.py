# Zope imports
from AccessControl import Unauthorized

# zope imports
from zope.interface import directlyProvides
from zope.component import provideUtility

# test imports
from base import RatingTestCase

# iqpp.rating imports
from iqpp.rating.interfaces import IRateable
from iqpp.rating.interfaces import IRatingManager
from iqpp.rating.interfaces import IRatingDefinition    
from iqpp.rating.content.definition import RatingDefinition

class TestRating(RatingTestCase):

    def testRate(self):
        rm = IRatingManager(self.portal.document)
        
        rm.rate(id=u"score", score=u"1", user=u"john")
        rm.rate(id=u"score", score=u"2", user=u"jane")
        rm.rate(id=u"score", score=u"3", user=u"ben")
                        
        rating = rm.getRating(id="score", user="john")
        self.assertEqual(rating, "1")

        rating = rm.getRating(id="score", user="jane")
        self.assertEqual(rating, "2")

        rating = rm.getRating(id="score", user="ben")
        self.assertEqual(rating, "3")

        ratings = rm.getRatings(id="score")
        self.assertEqual(len(ratings), 3)

        ratings = rm.getAmountOfRatings(id="score")
        self.assertEqual(ratings, 3)
        
        average = rm.getAverageRating(id="score")
        self.assertEqual(average, 2.0)

    def testNoRatings(self):
        rm = IRatingManager(self.portal.document)
        average = rm.getAverageRating(id="score")
        self.assertEqual(average, -1)
        
    def testWrongValue(self):
        rm = IRatingManager(self.portal.document)
        self.assertRaises(ValueError, rm.rate, id="score", score="42", user="john")

    def testWrongDefinition(self):
        rm = IRatingManager(self.portal.document)
        self.assertRaises(ValueError, rm.rate, id="wrong", score="1", user="john")

    def testChangeRating(self):
        rm = IRatingManager(self.portal.document)
        rm.rate(id=u"score", score=u"1", user=u"john")

        rating = rm.getRating(id=u"score", user=u"john")
        self.assertEqual(rating, "1")
        
        rm.rate(id=u"score", score=u"2", user=u"john")
        self.assertEqual(rating, "1")        

class TestRatingAsAnonymous(RatingTestCase):

    def testRate_1(self):
        """
        """
        rm = IRatingManager(self.portal.document)
        self.logout()
        
        rm.rate(id="score", user=None, score="1", ipaddress="127.0.0.1")
        rm.rate(id="score", user=None, score="2", ipaddress="127.0.0.2")
        rm.rate(id="score", user=None, score="3", ipaddress="127.0.0.3")

        self.login("test_user_1_")
        rating = rm.getRating(id="score")
        self.assertEqual(rating, 2.0)

        ratings = rm.getRatings(id="score")
        self.assertEqual(len(ratings), 1)

        ratings = rm.getAmountOfRatings(id="score")
        self.assertEqual(ratings, 3)
        
        average = rm.getAverageRating(id="score")
        self.assertEqual(average, 2.0)

    def testRate_2(self):
        rm = IRatingManager(self.portal.document)
        self.assertRaises(Unauthorized, rm.rate, id="score", score="1", user="john")
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRating))        
    # suite.addTest(makeSuite(TestRatingAsAnonymous))
    return suite
