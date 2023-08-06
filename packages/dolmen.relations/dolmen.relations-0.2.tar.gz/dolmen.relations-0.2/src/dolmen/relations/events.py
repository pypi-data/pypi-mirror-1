# -*- coding: utf-8 -*-

from zope.component.interfaces import ObjectEvent, IObjectEvent
from zope.interface import implements


class IRelationAddedEvent(IObjectEvent):
    """A relation has been added.
    """    

class IRelationDeletedEvent(IObjectEvent):
    """A relation has been deleted.
    """
    
class IRelationModifiedEvent(IObjectEvent):
    """A relation has been modified.
    """

class RelationAddedEvent(ObjectEvent):
    implements(IRelationAddedEvent)


class RelationDeletedEvent(ObjectEvent):
    implements(IRelationDeletedEvent)


class RelationModifiedEvent(ObjectEvent):
    implements(IRelationModifiedEvent)
