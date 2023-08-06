#!/usr/local/env/python
#############################################################################
# Name:         who
# Purpose:      Person and member related functions
# Maintainer:
# Copyright:    (c) 2004 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import zope.interface
import zope.proxy

from bebop.protocol import protocol
import bop.shortcut

import interfaces

members = protocol.GenericFunction('bop.who.IMembers')
@members.when(zope.interface.Interface)
def default_members(context):
    return {}

owns = protocol.GenericFunction('bop.who.IOwns')
@owns.when(zope.interface.Interface)
def default_owns(obj):
    dc = bop.shortcut.dc(obj, None)
    if dc is not None and dc.creators:
        return dc.creators[0]
    return None
 
realname = protocol.GenericFunction('bop.who.IRealname')
@realname.when(zope.interface.Interface, zope.interface.Interface)
def default_realname(principal_id, context):
    mems = members(context)
    if mems is not None:
        if principal_id in mems:
            return mems[principal_id].name
    return u'Anonymous'

authors = protocol.GenericFunction('bop.who.IAuthors')
@authors.when(zope.interface.Interface)
def default_authors(obj):
    bare = zope.proxy.removeAllProxies(obj)
    dc = bop.shortcut.dc(bare, None)
    if dc is not None and dc.creators:
        return dc.creators
    return None
        
authornames = protocol.GenericFunction('bop.who.IAuthors')
@authornames.when(zope.interface.Interface)
def default_authornames(obj):
    ids = authors(obj)
    if ids is not None:
        authornames = [realname(pid, obj) for pid in authors(obj)]
        return u', '.join(authornames)
    return None

contributors = protocol.GenericFunction('bop.who.IContributors')
@contributors.when(zope.interface.Interface)
def default_contributors(obj):
    bare =  zope.proxy.removeAllProxies(obj)
    dc = bop.shortcut.dc(bare, None)
    if dc is not None and dc.contributors:
        return dc.contributors
    return None

email = protocol.GenericFunction('bop.who.IEmail')
@email.when(zope.interface.Interface)
def default_email(obj):
    return None

class Who(protocol.Adapter):
    """Questions related to persons."""
    
    zope.interface.implements(interfaces.IWho)
    protocol.adapter(None, permission='zope.Public')
    
    @property
    def creator(self):
        return default_owns(self.context)
   
    @property
    def authors(self):
        return default_authors(self.context)
        
    @property
    def authornames(self):
        return authornames(self.context)
    
    @property
    def contributors(self):
        return contributors(self.context)    

    @property
    def email(self):
        return email(self.context)    


class Contributors(protocol.Adapter):
    """An adapter for contributors."""

    zope.interface.implements(interfaces.IContributors)
    protocol.adapter(None, permission='zope.Public')

    def getContributors(self):
        return contributors(self.context)
        
    def setContributors(self, contributors):
        bop.shortcut.dc(self.context).contributors = contributors

    contributors = property(getContributors, setContributors)
        
        
class TestMember(object):
    """A non-persistent member implementation for test purposes."""   

    zope.interface.implements(interfaces.IMember)
    
    def __init__(self,
            id=None, 
            name=u'Anonymous',
            email='nospam@please.org',
            portrait=None,
            ref=None):
        self.prinicpal_id = id
        self.name = name
        self.email = email
        self.portrait = portrait
        self.ref = ref
        


