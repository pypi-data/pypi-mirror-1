# -*- coding: utf-8 -*-

from BTrees.OOBTree import OOBTree

from zope.event import notify
from zope.interface import implements, alsoProvides
from zope.app.container.interfaces import IContained
from zope.app.container.constraints import checkObject

from dolmen.relations import events
from dolmen.relations import IRelationsContainer


class RelationsContainer(OOBTree):
    """A rough implementation of a relation storage.
    """
    implements(IRelationsContainer)
        
    def __setitem__(self, key, value):
        checkObject(self, key, value)
        value.__parent__ = self
        value.__name__ = key
        alsoProvides(value, IContained)
        OOBTree.__setitem__(self, key, value)
        notify(events.RelationAddedEvent(value))

    def __delitem__(self, key):
        notify(events.RelationDeletedEvent(self.get(key)))
        OOBTree.__delitem__(self, key)
 
