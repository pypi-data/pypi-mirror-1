#!/usr/local/env/python
#############################################################################
# Name:         permalink.py
# Purpose:      Permanent links based on shortrefs
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import zope.interface
import zope.security.proxy
import zope.publisher.browser
import zope.publisher.interfaces
import zope.app.file.interfaces

from bebop.protocol import protocol, browser

from bop import shortref
from bop import helper

import interfaces

url = protocol.GenericFunction('IPermalinkURL')
@url.when(None)
def default_url(obj):
    ref = shortref.ensureRef(obj)
    name = helper.asciiName(obj.__name__ or u'Unnamed')
    return '@@permalink/%s/%s' % (ref, name)

@url.when(zope.app.file.interfaces.IFile)
def file_url(obj):
    if obj.__name__ and obj.__name__.endswith('.webloc'):
        from bop.html import extractTagContent
        return extractTagContent(obj.data,'string')       
    else:
        return default_url(obj)
    
redirect = protocol.GenericFunction('IRedirect')
@redirect.when(None, None)
def default_redirect(context, request):
    return None


class TargetWrapper(zope.publisher.browser.BrowserView):
    """A view for a resolved permalink reference."""
    
    zope.interface.implements(zope.publisher.interfaces.IPublishTraverse)

    protocol.classProtocol.require(
        permission="zope.Public",
        interface=zope.publisher.interfaces.IPublishTraverse)

    def publishTraverse(self, request, name):
        return self.context

    
class Permalink(zope.publisher.browser.BrowserView):
    """A view that allows to traverse a permalink."""
    
    zope.interface.implements(zope.publisher.interfaces.IPublishTraverse)

    browser.page(zope.interface.Interface,
        name="permalink",
        permission="zope.Public")

    protocol.classProtocol.require(
        permission="zope.Public",
        interface=zope.publisher.interfaces.IPublishTraverse)
      
    def publishTraverse(self, request, ref):
        target = shortref.resolve(ref, self.context)
        if target is not None:
            return TargetWrapper(target, request)
        raise zope.publisher.interfaces.NotFound(self.context, ref)

