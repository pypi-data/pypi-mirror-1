#!/usr/local/env/python
#############################################################################
# Name:         bootstrap.py
# Purpose:      Ensures utilities for the use of Bebop
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################

import transaction
import zope.app.intid
import zope.app.appsetup
from zope.app.appsetup import bootstrap

import interfaces
import shortref
import bop

@bop.subscriber(zope.app.appsetup.IDatabaseOpenedEvent)
def bootstrapSubscriber(event):
    """Subscriber to the IDataBaseOpenedEvent

    Create utilities which are required for shortcuts etc.
    """
    db, connection, root, root_folder = bootstrap.getInformationFromEvent(event)
    
    before = zope.component.queryUtility(
        interfaces.IShortRefs,
        context=root_folder)
    
    bootstrap.ensureUtility(root_folder,
        zope.app.intid.interfaces.IIntIds,
        'IntIds',
         zope.app.intid.IntIds,
         asObject=True)
          
    bootstrap.ensureUtility(root_folder,
        interfaces.IShortRefs,
        'bebop.shortrefs',
        shortref.ShortRefs,
        asObject=True)
    if before is None:
        shortrefs = zope.component.queryUtility(
            interfaces.IShortRefs,
            context=root_folder)
        shortrefs.indexAll()
    
    transaction.commit()
    connection.close()

      

