# Zope imports
from DateTime import DateTime

# zope imports
from zope.interface import implements
from zope.component import adapts, queryUtility
from zope.app.annotation.interfaces import IAnnotations
from zope.event import notify as znotify
from BTrees.OOBTree import OOBTree


# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.rating imports
from iqpp.rating.content.rating import Rating
from iqpp.rating.content.rating import AnonymousRating
from iqpp.rating.events import Rated
from iqpp.rating.interfaces import IRateable
from iqpp.rating.interfaces import IRatingManager
from iqpp.rating.interfaces import IRatingDefinition

KEY1 = "iqpp.rating.members"
KEY2 = "iqpp.rating.anonymous"
KEY3 = "iqpp.rating.daily"

class RatingManager(object):
    """Adapter to manage ratings for arbitrary objects.
    """
    implements(IRatingManager)
    adapts(IRateable)
    
    def __init__(self, context):
        """
        """
        self.context = context    
        annotations = IAnnotations(context)
        
        self.member_ratings = annotations.get(KEY1)
        if self.member_ratings is None:
            self.member_ratings = annotations[KEY1] = OOBTree()

        self.anonymous_ratings = annotations.get(KEY2)
        if self.anonymous_ratings is None:
            self.anonymous_ratings = annotations[KEY2] = OOBTree()

        self.daily_ratings = annotations.get(KEY3)
        if self.daily_ratings is None:
            self.daily_ratings = annotations[KEY3] = {
                "last_rating" : DateTime().earliestTime()-1,
                "amount_of_ratings" : 0,
            }
        
    def deleteRating(self, id, user):
        """
        """
        try:
            del self.member_ratings[id][user]
        except KeyError:
            return False
        
        return True    
        
    def getAmountOfRatings(self, id=None):
        """
        """
        if id is None:
            id = self.getRatingId()
        
        amount_member_ratings = 0
        amount_anonymous_ratings = 0
        
        rating_definition = self.getRatingDefinition(id)
        
        member_ratings = self.member_ratings.get(id)
        if member_ratings is not None:            
            amount_member_ratings = len(member_ratings)
        
        anonymous_ratings = self.anonymous_ratings.get(id)
        if anonymous_ratings is not None:                
            amount_anonymous_ratings = anonymous_ratings.amount_of_ratings

        return amount_member_ratings + amount_anonymous_ratings

    def getAverageRating(self, id=None):
        """
        """
        if id is None:
            id = self.getRatingId()
        
        definition = self.getRatingDefinition(id)
                
        total_value  = 0
        total_amount = 0

        # member ratings
        ratings = self.member_ratings.get(id, {}).values()
        for rating in ratings:
            total_value  += definition.getNumericalValue(rating.score)
            total_amount += 1

        # anonymous ratings (weighted)
        rating = self.anonymous_ratings.get(id)
        if rating is not None:
            total_value  += (rating.average_rating * rating.amount_of_ratings)
            total_amount += rating.amount_of_ratings
            
        try:
            return "%.1f" % (total_value/total_amount)
        except ZeroDivisionError:
            return -1
            
    def getRatingDefinition(self, id):
        """
        """
        rating_definition = queryUtility(IRatingDefinition, id)
        if rating_definition is None:
            raise ValueError('No rating definition named %s found.' % id)

        return rating_definition

    def getRatings(self, id=None):
        """
        """
        if id is None:
            id = self.getRatingId()
        
        rating_definition = self.getRatingDefinition(id)
        ratings = list(self.member_ratings.get(id, {}).values())

        if self.anonymous_ratings.get(id) is not None:
            ratings.append(self.anonymous_ratings.get(id))
            
        return ratings
    
    def getRating(self, id=None, user=None):
        """
        """        
        if id is None:
            id = self.getRatingId()
        
        rating_definition = self.getRatingDefinition(id)
        if user is None:
            try:
                return self.anonymous_ratings[id].score
            except KeyError:
                return None
        else:    
            try:
                return self.member_ratings[id][user].score
            except KeyError:
                return None

    def getRatingId(self):
        """
        """
        try:
            return self.context.getRatingId()
        except AttributeError:
            return None
        
    def getScores(self, id=None):
        """
        """
        if id is None:
            id = self.getRatingId()
        
        scores = {}        
        
        member_ratings = self.member_ratings.get(id, {}).values()        
        for rating in member_ratings:
            if scores.has_key(rating.score) == False:
                scores[rating.score] = 0
            scores[rating.score] += 1    

        anonymous_ratings = self.anonymous_ratings.get(id)
        if anonymous_ratings is not None:        
            for score in anonymous_ratings.scores.keys():
                if scores.has_key(score) == False:
                    scores[score] = 0
                scores[score] += anonymous_ratings.scores.get(score)
        
        return scores

    def hasRated(self, id, user):
        """
        """
        if self.getRating(id, user) is not None:
            return True

        return False
        
    def rate(self, user, id, score, ipaddress=None, context=None, notify=True):
        """
        """
        rating_definition = self.getRatingDefinition(id)
        if not rating_definition.isValidScore(score):
            raise ValueError('Invalid rating score %s for %s.' % (score, id))
        
        # Anonymous user
        if user is None:
            if id not in self.anonymous_ratings:
                self.anonymous_ratings[id] = AnonymousRating(id)

            value = rating_definition.getNumericalValue(score)
            rating = self.anonymous_ratings[id]
            old_score = rating.score
            result = rating.addValue(value, score, ipaddress)
                        
            if result == True:            
                result = "rating-added"
                self._calcDailyRating()
            else:
                result = "already-rated"
        # Members
        else:                                
            if id not in self.member_ratings:
                self.member_ratings[id] = OOBTree()
            
            rating = self.member_ratings[id].get(user)
            if rating is None:
                old_score = 0
                result = "rating-added"
                self._calcDailyRating()
            else:
                old_score = rating.score
                result = "rating-changed"
            self.member_ratings[id][user] = Rating(id, score, user)

            # sent event
            if notify == True:
                if context is None: context = self.context
                znotify(Rated(old_score, score, user, self.context, context))

        self.context.reindexObject()
        return result
        
    def rateWithConfirmation(self):
        """
        """    
        # not implemented yet
     
    def setRating(self, score, id, user):
        """
        """
        # not implemented yet

    def _calcDailyRating(self):
        """
        """
        last_rating = self.daily_ratings["last_rating"]
        today = DateTime().earliestTime()
        if today - last_rating >= 1:
            self.daily_ratings["last_rating"] = DateTime().earliestTime()
            self.daily_ratings["amount_of_ratings"] = 0
            
        self.daily_ratings["last_rating"] = today
        self.daily_ratings["amount_of_ratings"] += 1
