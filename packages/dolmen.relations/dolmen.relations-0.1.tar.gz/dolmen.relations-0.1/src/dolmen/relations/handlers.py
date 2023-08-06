# -*- coding: utf-8 -*-

import grokcore.component as grok
from dolmen.relations import events, ICatalog, IRelationValue

from zope.interface import Interface
from zope.component import getUtility, adapter
from zope.interface import directlyProvides, noLongerProvides
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.intid.interfaces import IIntIds, IIntIdRemovedEvent


@grok.subscribe(IRelationValue, events.IRelationModifiedEvent)
def update_relation(relation, event):
    intids = getUtility(IIntIds)
    catalog = getUtility(ICatalog)
    catalog.unindex(relation)
    catalog.index_doc(intids.getId(relation), relation)


@grok.subscribe(IRelationValue, events.IRelationAddedEvent)
def add_relation(relation, event):
    """We index the relation then mark the source and target with
    the correct marker, to be sure it will trigger the events later.
    """
    intids = getUtility(IIntIds)
    catalog = getUtility(ICatalog)
    catalog.index_doc(intids.register(relation), relation)


@adapter(IIntIdRemovedEvent)
def object_deleted(event):
    
    ob = event.object
    catalog = getUtility(ICatalog, context=ob)
    
    if IRelationValue.providedBy(ob):
        # We assume relations can't be
        # source or targets of relations
        catalog.unindex(ob)
        return

    intids = getUtility(IIntIds, context=ob)
    uid = intids.queryId(ob)
    if uid is None:
	return
    
    rels = list(catalog.findRelations({'source_id': uid}))
    for rel in rels:
        parent = rel.__parent__
        try:
            catalog.unindex(parent[rel.__name__])
            del parent[rel.__name__]
        except KeyError:
            continue

    rels = list(catalog.findRelations({'target_id': uid}))
    for rel in rels:
        parent = rel.__parent__
        try:
            catalog.unindex(parent[rel.__name__])
            del parent[rel.__name__]
        except KeyError, e:
            continue
        
