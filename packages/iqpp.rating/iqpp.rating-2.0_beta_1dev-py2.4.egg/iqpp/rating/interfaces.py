# zope imports
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, Attribute
from zope.viewlet.interfaces import IViewletManager
from zope import schema
_ = MessageFactory("iqpp.rating")

class IRatingViewletManager(IViewletManager):
    """Viewlet manager for rating.
    """

class IRateable(IAttributeAnnotatable):
    """A marker interface marking an object as being ratable.
    """

class IRatingManager(Interface):
    """An interface which provides methods for rating arbitrary objects.
    """        
    def deleteRating(id, user):
        """Deletes the rating for the definition id and user. Returns True if 
        the rating was deleted, otherwise returns False.
        """
            
    def getAmountOfRatings(id):
        """Returns the total amount of ratings for the definition with given 
        id.
        """

    def getAverageRating(id):
        """Returns the average rating value for the definition with given id.
        """

    def getRatings(id):
        """Returns all ratings for the definition with the given id. Returns 
        a list of strings (member ratings) and a float (anonymous).
        """

    def getRating(id, user):
        """Returns a rating for the definition and user. Returns the ratings 
        for anoymous users if given user is None. Returns None if there is no
        rating (e.g. in order to differ zero from no rating).
        """

    def getRatingDefinition(id):
        """Returns the rating definition by given id.
        """
        
    def getRatingId():
        """Returns the rating id for an object. If the object has only one 
        rating, in this the passing of an rating id for every single request
        could be omitted.
        """
                
    def getScores(id):
        """Returns a dict of score : amount, whereas the keys are the scores 
        of the definition and the values are the amount of how often the score 
        was rated. If the score wasn't rated at all, it isn't within the dict.
        """

    def hasRated(id, user):    
        """Returns True if the given user has already rated for the given id.
        """

    def rate(user, id, score, ipaddress):
        """Adds a new rating with given informations.

        Parameters:
            id:    The id of the rating definition.
            score: The id of the score (not the value)        
        """

    def rateWithConfirmation(id, value, user):
        """Checks confirmation and calls the rate method.
        """

    def setRating(id, value, user):
        """Sets a value for a specific id and user. 
        """    
        
class IRating(Interface):
    """A single rating for a definition and user.
    """
    # TODO: Check this, as the id is the id of the rating definition atm. Should 
    # this rather stored in a definition field and additionally a unique id in the 
    # id field?
    id = schema.TextLine(title=_(u"Id"),
         description=_(u"The id of the rating"),
         required=True,   
    )

    score = schema.TextLine(title=_(u"Score"),
         description=_(u"The score which has been rated."),
         required=True,   
    )

    user = schema.TextLine(title=_(u"User"),
         description=_(u"The user who has rated."),
         required=True,   
    )

    timestamp = schema.Datetime(title=_(u"Timestamp"),
         description=_(u"When has been rated"),
         required=True,   
    )

class IAnonymousRating(IRating):
    """Total rating of anonymous users for a specific definition.
    """
    amount_of_ratings = schema.Int(title=_(u"Amount of ratings"),
         description=_(u"The total amount of ratings"),
         required=True,   
         default=0,
    )

    average_rating = schema.Float(title=_(u"Average rating"),
         description=_(u"The average rating"),
         required=True,
         default=0.0,  
    )

    # TODO: Make these as schema fields to give an admin the possibility to 
    # change ratings in future.
    ipaddresses = Attribute("The ip address with which was been rated.")
    scores = Attribute("The scores which have been rated.")
        
    def hasRated(ipaddress):
        """Returns True if the given ip address has already rated.
        """
            
    def addValue(self, value, ipaddress):
        """Adds a value and calculates the new value (which is the average 
        rating over all added ratings. Takes also care of the amount of
        ratings.)
        """

class IRatingDefinition(Interface):
    """A definition for a rating.
    """
    
    def isValidScore(score):
        """Returns true if the given score is valid for this definition.
        """
        
    def getNumericalValue(score):
        """Returns the numerical value for a given score.
        """

class IRated(Interface):
    """A marker interface for the event: user has rated.
    """
        
class IRatingOptions(Interface):
    """Provides a schema for rating options.
    """
    is_enabled = schema.Bool(title=_(u"Enabled"),
         description=_(u"Is rating enabled?"),
         default=True,
    )
    
    score_card = schema.Text(
        title=_(u'The Score Card'),
        description=_(u"The score card. One title:value pair per line."),
        default=u'',
        required=True)
    
    