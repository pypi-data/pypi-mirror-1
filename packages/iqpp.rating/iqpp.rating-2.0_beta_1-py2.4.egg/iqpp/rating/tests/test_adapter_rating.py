# Zope imports
from DateTime import DateTime
from BTrees.OOBTree import OOBTree

# test imports
from base import RatingTestCase

# iqpp.rating imports
from iqpp.rating.interfaces import IRateable
from iqpp.rating.interfaces import IRatingManager
from iqpp.rating.interfaces import IRatingDefinition    
from iqpp.rating.content.definition import RatingDefinition

class TestRatingManager(RatingTestCase):
    """
    """                        
    def testInitialization(self):
        """
        """
        rm = IRatingManager(self.portal.document)        
        daily = rm.daily_ratings

        self.failUnless(len(rm.member_ratings) == 0)
        self.failUnless(isinstance(rm.member_ratings, OOBTree))
        
        self.failUnless(len(rm.anonymous_ratings) == 0)
        self.failUnless(isinstance(rm.anonymous_ratings, OOBTree))
        
        # daily ratings
        self.assertEqual(daily["last_rating"], DateTime().earliestTime()-1)
        self.assertEqual(daily["amount_of_ratings"], 0)

    def testRate_1(self):
        """Test rating generally.
        """    
        rm = IRatingManager(self.portal.document)        
        rm.rate(id=u"score", score=u"1", user=u"john")
        rm.rate(id=u"score", score=u"2", user=u"jane")
        rm.rate(id=u"score", score=u"3", user=u"ben")

        rm = IRatingManager(self.portal.document)        
        daily = rm.daily_ratings
        self.assertEqual(daily["last_rating"], DateTime().earliestTime())
        self.assertEqual(daily["amount_of_ratings"], 3)

    def testRate_2(self):
        """Test daily ratings
        """    
        rm = IRatingManager(self.portal.document)
        rm.rate(id=u"score", score=u"1", user=u"john")
        rm.rate(id=u"score", score=u"2", user=u"jane")
        rm.rate(id=u"score", score=u"3", user=u"ben")

        rm = IRatingManager(self.portal.document)
        daily = rm.daily_ratings

        # Move ratings back on day ...
        yesterday = DateTime()-1
        daily["last_rating"] = yesterday.earliestTime()

        # ... so that they here get deleted.
        rm.rate(id=u"score", score=u"1", user=u"jonny")                
        self.assertEqual(daily["last_rating"], DateTime().earliestTime())
        self.assertEqual(daily["amount_of_ratings"], 1)
        
    def testGetRatings_1(self):
        """Just member ratings
        """
        rm = IRatingManager(self.portal.document)        
        rm.rate(id=u"score", score=u"1", user=u"john")
        rm.rate(id=u"score", score=u"2", user=u"jane")
        rm.rate(id=u"score", score=u"3", user=u"ben")
    
        ratings = rm.getRatings(id="score")
        self.assertEqual(len(ratings), 3)
                
        scores = [r.score for r in ratings]
    
        self.failUnless(u"1" in scores)
        self.failUnless(u"2" in scores)        
        self.failUnless(u"3" in scores)
            
    def testGetRating(self):
        """
        """        
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
    
    def testGetRatingId(self):
        """
        """
    
    def testGetAmountOfRatings(self):
        """
        """
    
    def testGetAverageRating(self):
        """
        """
    
    def testGetScores(self):
        """
        """
    
    def testHasRated(self):
        """
        """
        
    def testDeleteRating(self):
        """
        """
    
    def testSetRating(self):
        """
        """
        # not implemented yet    
        
    def testRateWithConfirmation(self):
        """
        """    
        # not implemented yet
        
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRatingManager))        
    return suite
