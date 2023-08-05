# zope imports
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingOptions
from iqpp.rating.interfaces import IRatingOptionsSchema
from iqpp.rating.interfaces import IRateable

KEY = "iqpp.rating.options"

class RatingOptions(object):
    """An adapter which provides IRatingOptions for ratable objects.
    """
    adapts(IRateable)

    def __init__(self, context):
        """
        """
        self.context = context

        annotations = IAnnotations(context)
        options = annotations.get(KEY)

        if options is None:
            options = annotations[KEY] = {
                'options'   : PersistentDict(),
                'overrides' : PersistentList(),
            }

        self.options   = options['options']
        self.overrides = options['overrides']

    def getEffectiveOption(self, name):
        """
        """
        if name in self.overrides:
            return self._named_get(name)
        else:
            return self.getGlobalOption(name)

    def getGlobalOption(self, name):
        """
        """
        return IRatingOptions[name].default

    @apply
    def is_enabled():
        def get(self): return self._named_get('is_enabled')
        def set(self, value): self._named_set('is_enabled', value)
        return property(get, set)

    @apply
    def score_card():
        def get(self): return self._named_get('score_card')
        def set(self, value): self._named_set('score_card', value)
        return property(get, set)
        
    def _named_get(self, name):
        """Returns the local option with given name.
        """
        return self.options.get(name, None)
            
    def _named_set(self, name, value):
        """Sets the local option for the given name.
        """
        if name not in self.overrides:
            self.overrides.append(name)
        self.options[name] = value