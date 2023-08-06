#!/usr/bin/python
#############################################################################
# Name:         rdf.py
# Purpose:      Implements RDF converter for orderable objects
# Maintainers:  Uwe Oestermeier <u.oestermeier@iwm-kmrc.de>
# Copyright:    (c) iwm-kmrc.de KMRC - Knowledge Media Research Center
# License:      GPLv2
#############################################################################
__docformat__ = 'restructuredtext'

import zope.interface
import zope.app.container.interfaces
from bop import rdf
import bop
import interfaces


class OrderableConverter(rdf.SchemaConverter):
    """Converts the order attribute into RDF predicate."""
    
    bop.adapter(
        zope.app.container.interfaces.IContained,
        zope.interface.Interface,
        provides=bop.interfaces.IRDFConverter,
        name='bop:ordering')

    namespace = rdf.bopns
    interface = interfaces.IOrderable

