#!/usr/local/env/python
#############################################################################
# Name:         where
# Purpose:      Location related functions and adapters
# Maintainer:
# Copyright:    (c) 2004 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.app.container.interfaces
import zope.app.intid.interfaces

from bebop.protocol import protocol
import bop.shortcut
import bop.helper
import interfaces

class Where(protocol.Adapter):
    """An adapter for locations specific infos.
    
    Uese int ids for efficient indexing.
    """
    
    zope.interface.implements(interfaces.IWhere)
    protocol.adapter(
        zope.app.container.interfaces.IContained,
        permission='zope.Public')

    @property
    def here(self) :
        """ Returns the intId of self. """
        utility = bop.query(
            zope.app.intid.interfaces.IIntIds,
            context=self.context)
        if utility is not None:
            return utility.register(self.context)
        return None
    
    @property
    def locations(self) :
        locs = set()
        intIds = bop.query(
            zope.app.intid.interfaces.IIntIds,
            context=self.context)
        if intIds is None:
            return locs
            
        def collect(node):
            while node is not None:
                locs.add(intIds.register(node))
                node = node.__parent__
            
        collect(self.context)
        return locs
    
