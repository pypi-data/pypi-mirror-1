iqpp.rating Package Readme
=========================

Overview
--------
Enables rating for arbitrary Plone stuff.

Disclaimer
----------
This package is strongly inspired on lovely.ratings and couldn't be done so 
easily without that. OTH some heavily changes are introduced by me during the
development process. IOW: Kudos and thanks to lovely and please don't blame 
them for any bugs or stupid things.

Further more catWorkX (http://www.catworkx.de) payed me for the developing of 
this package and allowed me kindly to put this open source.

Quickstart
----------
To use it we have first to create a rating definition.

    >>> from zope.component import provideUtility
    >>> from iqpp.rating.definition import RatingDefinition
    >>> from iqpp.rating.interfaces import IRatingDefinition    
    
    >>> sc = [("1", 1.0), ("2", 2.0), ("3", 3.0), ("4", 4.0),  ("5", 5.0),  ("6", 6.0)]
    >>> score = RatingDefinition("Score", sc, "The Score for a Paper")
    >>> provideUtility(score, IRatingDefinition, name='score')
    
Let's see whether it works probably.

    >>> from zope.component import queryUtility
    >>> definition = queryUtility(IRatingDefinition, "score")

Do we got the definition?
    
    >>> definition
    <iqpp.rating.definition.RatingDefinition instance at ...>

To prevent manipulations, there are only valid scores allowed. 

    >>> definition.isValidScore("3")
    True

    >>> definition.isValidScore("42")
    False

To be able to make calculations one can retrieve the numerical value of a 
given score.
    
    >>> definition.getNumericalValue("2")
    2.0
    
Now let's create a document, which should be able to be rated with above
created definition scores.

    >>> self.folder.invokeFactory("Document", "document")
    'document'

Mark the document as ratable.
    
    >>> from zope.interface import directlyProvides
    >>> from iqpp.rating.interfaces import IRateable
    >>> directlyProvides(self.folder.document, IRateable)
    
Now get the RatingManager for this document ...

    >>> from iqpp.rating.interfaces import IRatingManager
    >>> rm = IRatingManager(self.folder.document)
    
... and do some ratings.    

    >>> rm.rate(id="score", score="1", user="john")
    'rating-added'
    >>> rm.rate(id="score", score="2", user="jane")
    'rating-added'
    >>> rm.rate(id="score", score="3", user="ben")
    'rating-added'

Let's get the ratings back.

    >>> rm.getRating(id="score", user="john")
    '1'

    >>> rm.getRating(id="score", user="jane")
    '2'

    >>> rm.getRating(id="score", user="ben")
    '3'
    
    >>> len(rm.getRatings(id="score"))
    3
    
    >>> rm.getAmountOfRatings(id="score")
    3
    
    >>> rm.getAverageRating(id="score")
    2.0
    