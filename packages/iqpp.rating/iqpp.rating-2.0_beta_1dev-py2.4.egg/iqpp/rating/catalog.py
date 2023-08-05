# zope imports
from zope.component.exceptions import ComponentLookupError

# CMFPlone imports
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingManager

def average_rating(object, portal, **kwargs):
    try:
        return IRatingManager(object).getAverageRating("plone")            
    except (ComponentLookupError, TypeError, ValueError):
        raise AttributeError

def amount_of_ratings(object, portal, **kwargs):
    try:
        return IRatingManager(object).getAmountOfRatings("plone")            
    except (ComponentLookupError, TypeError, ValueError):
        raise AttributeError

def last_rating(object, portal, **kwargs):
    try:
        return IRatingManager(object).daily_ratings["last_rating"]
    except (ComponentLookupError, TypeError, ValueError):
        raise AttributeError

def daily_amount_of_ratings(object, portal, **kwargs):
    try:
        return IRatingManager(object).daily_ratings["amount_of_ratings"]
    except (ComponentLookupError, TypeError, ValueError):
        raise AttributeError
        
registerIndexableAttribute('average_rating', average_rating)
registerIndexableAttribute('amount_of_ratings', amount_of_ratings)            
registerIndexableAttribute('last_rating', last_rating)
registerIndexableAttribute('daily_amount_of_ratings', daily_amount_of_ratings)            