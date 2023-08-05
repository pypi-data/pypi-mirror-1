# zope imports
from zope.interface import implements

# iqpp imports
from iqpp.rating.interfaces import IRatingDefinition

class RatingDefinition:
    """Defines scores and corresponding numerical values.
    """
    
    implements(IRatingDefinition)

    def __init__(self, title, scores, description=None):
        """
        """
        self.title = title
        self.scores = scores
        if description is not None:
            self.description = description

    def isValidScore(self, score):
        """
        """
        if score in [s[0] for s in self.scores]:
            return True
        return False
        
    def getNumericalValue(self, score):
        """
        """
        for s in self.scores:
            if s[0] == score:
                return s[1]
        return 0
