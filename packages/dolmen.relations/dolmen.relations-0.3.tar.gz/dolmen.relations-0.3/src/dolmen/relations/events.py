# -*- coding: utf-8 -*-

from zope.component.interfaces import ObjectEvent, IObjectEvent
from zope.lifecycleevent.interfaces import (
    IObjectAddedEvent, IObjectRemovedEvent)
from zope.lifecycleevent import ObjectAddedEvent, ObjectRemovedEvent
from zope.interface import implements


class IRelationAddedEvent(IObjectAddedEvent):
    """A relation has been added.
    """

class IRelationDeletedEvent(IObjectEvent):
    """A relation has been deleted.
    """

class IRelationModifiedEvent(IObjectRemovedEvent):
    """A relation has been modified.
    """

class RelationAddedEvent(ObjectAddedEvent):
    implements(IRelationAddedEvent)


class RelationDeletedEvent(ObjectRemovedEvent):
    implements(IRelationDeletedEvent)


class RelationModifiedEvent(ObjectEvent):
    implements(IRelationModifiedEvent)
