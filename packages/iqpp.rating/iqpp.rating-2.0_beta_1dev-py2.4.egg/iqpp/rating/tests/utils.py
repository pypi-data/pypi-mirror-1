# zope imports 
from zope.component import provideUtility
from zope.interface import implements

# iqpp.rating imports
from iqpp.rating.interfaces import IRateable
from iqpp.rating.interfaces import IRatingDefinition
from iqpp.rating.content.definition import RatingDefinition

def createDefinition():
    """
    """
    sc = [("1", 1.0), ("2", 2.0), ("3", 3.0), ("4", 4.0),  ("5", 5.0),  ("6", 6.0)]
    score = RatingDefinition("Score", sc, "The Score for a Paper")
    provideUtility(score, IRatingDefinition, name='score')