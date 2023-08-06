#!/usr/local/env/python
#############################################################################
# Name:         tests.py
# Purpose:      Holds tests of the bebop.ordering package  
# Maintainer:
# Copyright:    (c) 2004 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import unittest, zope, os, shutil

import zope.component
import zope.annotation

from zope.testing import doctest, doctestunit
from zope.app.testing import setup
from zope.app.testing import ztapi
from zope.interface import classImplements

from zope.dublincore.interfaces import IZopeDublinCore
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter

from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation.interfaces import IAnnotations, IAnnotatable
from zope.annotation.attribute import AttributeAnnotations
from zope.copypastemove import ContainerItemRenamer
from zope.copypastemove.interfaces import IContainerItemRenamer
from zope.copypastemove.interfaces import IObjectMover
from zope.copypastemove import ObjectMover
from zope.copypastemove.interfaces import IObjectCopier
from zope.copypastemove import ObjectCopier
from zope.size.interfaces import ISized
from zope.size import DefaultSized
from zope.traversing.interfaces import ITraversable, ITraverser
from zope.traversing.interfaces import IPhysicallyLocatable
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.adapters import RootPhysicallyLocatable
from zope.traversing.adapters import Traverser
from zope.location.traversing import LocationPhysicallyLocatable
from zope.location.interfaces import ISublocations

from zope.app.container.interfaces import IContained
from zope.app.container.interfaces import IContainer
from zope.app.file.interfaces import IFile
from zope.app.folder import Folder
from zope.app.folder.interfaces import IFolder
from zope.app.file.file import File
from zope.app.folder.folder import Folder
from zope.app.container.interfaces import IReadContainer
from zope.app.container.contained import ContainerSublocations        
        
from bebop.ordering.interfaces import IOrderable
from bebop.ordering.interfaces import IOrdering
from bebop.ordering.ordering import Ordering
from bebop.ordering.orderable import Orderable

 
def buildOrderingTestFolder():    
    myfold = Folder()
    myfold["a"]=Folder()
    myfold["b"]=Folder()    
    myfold["c"]=Folder()
    myfold["d"]=Folder()
    myfold["e"]=Folder()
    myfold["f"]=Folder()    
    
    return myfold

def registerDefaultAdapter():

    classImplements(File, IAnnotatable)
    classImplements(Folder, IAnnotatable)
    classImplements(File, IAttributeAnnotatable)
    classImplements(Folder, IAttributeAnnotatable)
    
    ztapi.provideAdapter(None, ITraverser, Traverser)
    ztapi.provideAdapter(None, ITraversable, DefaultTraversable)
    ztapi.provideAdapter(None, IPhysicallyLocatable,
                                LocationPhysicallyLocatable)
    ztapi.provideAdapter(IContainmentRoot, IPhysicallyLocatable, 
                                RootPhysicallyLocatable)

    ztapi.provideAdapter(IAnnotatable, IZopeDublinCore, ZDCAnnotatableAdapter)
    ztapi.provideAdapter(IAnnotatable, IAnnotations, AttributeAnnotations)
    ztapi.provideAdapter(IContainer, IContainerItemRenamer,
                                ContainerItemRenamer)
    ztapi.provideAdapter(ISublocations, IReadContainer, ContainerSublocations)                            

    classImplements(File, IAnnotatable)
    classImplements(Folder, IAnnotatable)
    
    ztapi.provideAdapter(IAnnotatable, IAnnotations, AttributeAnnotations )
    ztapi.provideAdapter(IContainer, IContainerItemRenamer,
                                ContainerItemRenamer)
    ztapi.provideAdapter(None, IObjectMover, ObjectMover)
    ztapi.provideAdapter(None, IObjectCopier, ObjectCopier) 
    
    ztapi.provideAdapter(None, ISized, DefaultSized) 

    ztapi.provideAdapter(IFolder, IOrdering, Ordering)


    zope.component.provideAdapter(zope.annotation.factory(Orderable))

  
def setUp(test):
    setup.placefulSetUp()
    registerDefaultAdapter()
    
def tearDown(test):
    setup.placefulTearDown()
    

def test_suite():    
    return unittest.TestSuite((
       doctest.DocTestSuite("bebop.ordering.ordering", 
                                           setUp=setUp, 
                                           tearDown=tearDown),
       doctest.DocTestSuite("bebop.ordering.orderable", 
                                           setUp=setUp, 
                                           tearDown=tearDown),                                    
       ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

