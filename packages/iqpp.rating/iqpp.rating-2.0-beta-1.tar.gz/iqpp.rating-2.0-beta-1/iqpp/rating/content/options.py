# zope imports
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# Zope imports
from OFS.SimpleItem import SimpleItem

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingOptions

class RatingOptionsStorage(SimpleItem):
    """Stores global rating options.
    """
    implements(IRatingOptions)    
    is_enabled = FieldProperty(IRatingOptions['is_enabled'])
    score_card = FieldProperty(IRatingOptions['score_card'])