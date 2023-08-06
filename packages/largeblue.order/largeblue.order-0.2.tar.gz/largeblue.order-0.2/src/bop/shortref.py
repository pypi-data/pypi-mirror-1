#!/usr/local/env/python
#############################################################################
# Name:         shortref.py
# Purpose:      Permanent human readable object references
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import persistent
import transaction
import BTrees
import BTrees.OOBTree
import zope.interface
import zope.location.interfaces
import zope.app.container.contained 
import zope.app.keyreference.interfaces

import interfaces
import bop

def ref(ob, context=None):
    if context is None:
        context = ob
    utility = bop.query(interfaces.IShortRefs, context=context)
    if utility is not None:
        try:
            return utility.getId(ob)
        except KeyError:
            return None

def ensureRef(ob, context=None):
    if context is None:
        context = ob
    utility = bop.query(interfaces.IShortRefs, context=context)
    if utility is not None:
        try:
            return utility.getId(ob)
        except KeyError:
            utility.register(ob)    
            return utility.getId(ob)
    else:
        bop.warning('Cannot find shortref utility.')

def resolve(ref, context):
    """Resolves the given ref in the context."""
    utility = bop.query(interfaces.IShortRefs, context=context)
    if utility is not None:
        try:
            return utility.getObject(ref)
        except KeyError:
            return None
        except interfaces.InvalidShortRef:
            return None
    
class IntMapping(zope.app.intid.IntIds):
    """A specialization of the IntIds utility which starts with 1"""
    counter = 1
    
    def _generateId(self):
        """Generate an id which is not yet taken.
        """
        while True:
            uid = self.counter
            if uid not in self.refs:
                return uid
            self.counter += 1
            

class ShortRefs(persistent.Persistent, zope.app.container.contained.Contained):
    """This utility provides a two way mapping between objects and
    permanent ids for each involved object class name.

    IKeyReferences to objects are stored in the indexes.
    """
    zope.interface.implements(interfaces.IShortRefs)

    def __init__(self):
        self.mappings = BTrees.OOBTree.OOBTree()
        
    def prefix(self, ob):
        return ob.__class__.__name__.lower()
        
    def split(self, id):
        i = len(id)-1
        tail = ''
        while id and i and id[i].isdigit():
            tail = id[i] + tail
            i -= 1
        head = id[:i+1]
        try:
            return head, int(tail)
        except ValueError:
            raise interfaces.InvalidShortRef(id)
        
    def getObject(self, id):
        head, tail = self.split(id)
        return self.mappings[head].getObject(tail)

    def queryObject(self, id, default=None):
        head, tail = self.split(id)
        r = self.mappings.get(head)
        if r is not None:
            return r.queryObject(tail)
        return default

    def getId(self, ob):
        head = self.prefix(ob)
        r = self.mappings.get(head)
        try:
            return '%s%s' % (head, self.mappings[head].getId(ob))
        except KeyError:
            raise KeyError(ob)

    def queryId(self, ob, default=None):
        try:
            return self.getId(ob)
        except KeyError:
            return default

    def register(self, ob):
        head = self.prefix(ob)
        if head not in self.mappings:
            self.mappings[head] = IntMapping()
        uids = self.mappings[head] 
        return uids.register(ob)

    def unregister(self, ob):
        head = self.prefix(ob)
        uids = self.mappings[head] 
        return uids.unregister(ob)
        
    def indexAll(self):
        site = bop.site(self)
        self.register(site)
        for sub in bop.sublocations(site, recursively=True):
            self.register(sub)

    def reindexAll(self):
        for key, mapping in self.mappings.items():
            for obj in mapping:
                self.unregister(obj)
        self.indexAll()


def unregisterRef(ob):
    utility = bop.query(interfaces.IShortRefs, context=ob)
    if utility is not None:
        try:
            utility.unregister(ob)
        except KeyError:
            pass

            
@bop.subscriber(
    zope.location.interfaces.ILocation,
    zope.app.container.interfaces.IObjectRemovedEvent)
def removeShortRefSubscriber(ob, event):
    """A subscriber to ObjectRemovedEvent

    Removes the unique ids registered for the object in all the unique
    id utilities. Postpones the removal to the beforeCommitHook since
    before commit events may refer to removed objects.
    
    """
    t = transaction.get()
    t.addBeforeCommitHook(unregisterRef, (ob,))

    
@bop.subscriber(
    zope.location.interfaces.ILocation,
    zope.app.container.interfaces.IObjectAddedEvent)
def addShortRefSubscriber(ob, event):
    """A subscriber to ObjectAddedEvent

    Registers the object added in all unique id utilities and fires
    an event for the catalogs.
    """
    if interfaces.IShortRefs.providedBy(ob):
        ob.reindexAll()
    utility = bop.query(interfaces.IShortRefs, context=ob)
    if utility is not None:
        utility.register(ob)



