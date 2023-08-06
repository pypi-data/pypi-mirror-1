import unittest, doctest, shutil

from zope.app.testing import placelesssetup, ztapi
from zope.testing.doctestunit import DocFileSuite

from zope import interface, component
from zope.lifecycleevent import IObjectModifiedEvent
from zope.app.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent

import transaction

import interfaces, subscriber, operation

def setUp( test ):
    placelesssetup.setUp()
    
    ztapi.provideAdapter( interfaces.IIndexable, 
                          interfaces.IOperationFactory,
                          operation.OperationFactory
                          )

    
    ztapi.subscribe( (interfaces.IIndexable, IObjectAddedEvent),
                     None,
                     subscriber.objectAdded )

    ztapi.subscribe( (interfaces.IIndexable, IObjectModifiedEvent),
                     None,
                     subscriber.objectModified )    

    ztapi.subscribe( (interfaces.IIndexable, IObjectRemovedEvent),
                     None,
                     subscriber.objectDeleted )    

def tearDown( test ):
    placelesssetup.tearDown()
    shutil.rmtree('tmp.idx')
    
def test_suite( ):

    globs = dict( implements = interface.implements,
                  component  = component,
                  transaction = transaction,
                  interfaces = interfaces )
    
    return unittest.TestSuite((
        DocFileSuite('readme.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     globs=globs,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),    
        ))

