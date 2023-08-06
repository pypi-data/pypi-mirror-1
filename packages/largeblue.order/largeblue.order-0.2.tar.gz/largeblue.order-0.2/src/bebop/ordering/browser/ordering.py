#!/usr/local/env/python
#############################################################################
# Name:         .py 
# Last Modified $Date: 2005-06-14 14:51:06 +0200 (Di, 14 Jun 2005) $ 
# $Rev: 605 $
# Last Modified by $Author: knobloch $
# Purpose:      View for IOrderable 
# Maintainer:
# Copyright:    (c) 2004,2005 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
# 
##############################################################################
import unittest
from zope.testing import doctest

from zope.interface import implements
import sys

from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation.interfaces import IAnnotations, IAnnotatable
from zope.annotation.attribute import AttributeAnnotations
from zope.publisher.browser import BrowserView

from zope.app import zapi
from zope.app.container.interfaces import IContained

from bebop.ordering.interfaces import IOrderable, IOrdering
from bebop.ordering.ordering import Ordering


class OrderingView(BrowserView):
    """
    View class using adapter to show items of displayed container
    in ordered form
    
    >>> from kmrc.bebop.adapter.tests import buildOrderingTestFolder
    >>> myfold = buildOrderingTestFolder()
    >>> view = OrderingView(myfold,None)
    >>> for n in view.orderingcontext.values():
    ...    print n.order, n.context.__name__
    0 a
    1 b
    2 c
    3 d
    4 e
    5 f
    
    """
    error = ''
    def __init__(self,context,request):
        super(OrderingView,self).__init__(context, request)
        self.orderingcontext = Ordering(context)
        
    def listContentInfo(self):       
        request = self.request
        ordering = self.orderingcontext
        
        # retrieve requested action
        action = None
        if u"orderable_up" in request:
            action = ordering.upOne
        elif u"orderable_top" in request:
            action = ordering.goTop
        elif u"orderable_down" in request:
            action = ordering.downOne
        elif u"orderable_bottom" in request:
            action = ordering.goBottom
            
        # perform moving action if ids are selected and an action 
        # indicator was in request
        #ids = [int(x) for x in request.get('ids')]
        ids = request.get('ids')
        if action:
            if not ids:
                self.error = "You didn't specify any ids to remove."
                return

            action([int(x) for x in ids]) #perform moving action 
            
        # return the dicts for the view pt in correct order
        # like _normallistcontents
        for n in range(len(self.context)):
            item = ordering.getItemFromPosition(n) #self.items[n]
            context = item.__parent__
            zmi_icon = zapi.queryMultiAdapter((context, self.request), name='zmi_icon')
            if zmi_icon is not None:
                zmi_icon = zmi_icon()
            
            yield dict(id = context.__name__,   #items name
                       cb_id = item.getOrder(), #checkboxid
                       url = zapi.absoluteURL(context, self.request),
                       icon = zmi_icon)
       

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')