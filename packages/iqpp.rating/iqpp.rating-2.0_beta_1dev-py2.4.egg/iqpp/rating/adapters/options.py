# zope imports
from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingOptions
from iqpp.rating.interfaces import IRateable
from iqpp.rating.content.options import RatingOptionsStorage

KEY = "iqpp.rating.options"
                
class RatingOptions(object):
    """An adapter which provides IRatingOptions for ratable objects.    
    """
        
    # Global options are stored in RatingOptionsStorage, local are stored as 
    # annotations within the context. We try first to get a local option. If 
    # there is none, we take the global opions.
    
    implements(IRatingOptions)
    adapts(IRateable)

    def __init__(self, context):
        """
        """
        self.context = context
        self.annotations = IAnnotations(context).get(KEY, None)
        if self.annotations is None:
            self.annotations = IAnnotations(context)[KEY] =\
                {'options' : RatingOptionsStorage(), 'overrides' : []}

        self.options = self.annotations['options']
        self.overrides = self.annotations['overrides']

    def getGlobalOption(self, name):
        """3rd-party products may override this method to take their global 
        options from somewhere else, e.g. a configlet. See iqpp.plone.rating 
        for more.
        """
        return IRatingOptions.get(name).default

    def getLocalOption(self, name):
        """3rd-party products may override this method to take their local 
        options from somewhere else, e.g. a configlet. See iqpp.plone.rating 
        for more.
        """
        return getattr(self.options, name)        
        
    def named_get(self, name):
        if name in self.overrides:
            return self.getLocalOption(name)
        else:
            return self.getGlobalOption(name)

    def named_set(self, name, value):
        if name not in self.overrides:
            self.overrides.append(name)
        setattr(self.options, name, value)
        
    @apply
    def is_enabled():
        def get(self): return self.named_get('is_enabled')
        def set(self, value): self.named_set('is_enabled', value)
        return property(get, set)
        
    @apply
    def score_card():
        def get(self): return self.named_get('score_card')
        def set(self, value): self.named_set('score_card', value)
        return property(get, set)