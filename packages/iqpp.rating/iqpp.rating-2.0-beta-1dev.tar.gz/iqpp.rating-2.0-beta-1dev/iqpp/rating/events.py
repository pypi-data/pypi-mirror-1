# zope imports
from zope.interface import implements
from zope.app.event.objectevent import ObjectModifiedEvent

# iqpp imports
from iqpp.rating.interfaces import IRated

class Rated(ObjectModifiedEvent):
    """An Event, which is fired up when a user has rated.
    """
    implements(IRated)
    
    def __init__(self, old_score, score, user, object, context=None):
        """
        """
        self.old_score  = old_score
        self.score  = score
        self.object = object  
        self.user = user
        self.context = context