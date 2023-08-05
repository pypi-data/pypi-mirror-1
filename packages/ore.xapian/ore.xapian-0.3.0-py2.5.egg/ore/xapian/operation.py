"""
$Id: $
"""

from zope import component, interface

import time
import xappy
import interfaces
import queue

class IndexOperation( object ):
    """
    an async/queued index operation
    """

    interface.implements( interfaces.IIndexOperation )

    __slots__ = ('oid', 'resolver_id',)
    
    def __init__( self, oid, resolver_id ):
        self.oid = oid
        self.resolver_id = resolver_id

    def resolve( self ):
        if self.resolver_id:
            resolver = component.getUtility( interfaces.IResolver , self.resolver_id ) 
        else:
            resolver = component.getUtility( interfaces.IResolver )
        instance = resolver.resolve( self.oid )
        return instance

    def process( self, connection ):
        raise NotImplemented

    @property
    def document_id( self ):
        return self.oid

    def store( self ):
        queue.index_queue.put( self )

class AddOperation( IndexOperation ):

    def process( self, connection ):
        instance = self.resolve()
        doc = interfaces.IIndexer( instance ).document( connection )
        doc.id = self.document_id
        doc.fields.append( xappy.Field('resolver', self.resolver_id or '' ) )
        connection.add( doc )
        
class ModifyOperation( IndexOperation ):

    def process( self, connection ):
        # XXX we have an issue where the async processor is ready to process
        # before the session/transaction modifying the object is even complete
        # ideally we should provide transactional dispatch of queue operations,
        # for now just make sure we sleep.. XXX MAJOR HACK.
        time.sleep(1)
        instance = self.resolve()
        doc = interfaces.IIndexer( instance ).document( connection )
        doc.id = self.document_id        
        doc.fields.append( xappy.Field('resolver', self.resolver_id ) )
        connection.replace( doc )
    
class DeleteOperation( IndexOperation ):

    def process( self, connection ):
        connection.delete( self.document_id )

class OperationFactory( object ):

    interface.implements( interfaces.IOperationFactory )

    __slots__ = ('context',)

    resolver_id = '' # default resolver

    def __init__( self, context ):
        self.context = context
    
    def add( self ):
        return AddOperation( *self._id() )

    def modify( self ):
        return ModifyOperation( *self._id() )

    def remove( self ):
        return DeleteOperation( *self._id() )
        
    def _id( self ):
        if self.resolver_id:
            resolver = component.getUtility( interfaces.IResolver , self.resolver_id ) 
        else:
            resolver = component.getUtility( interfaces.IResolver )
        oid = resolver.id( self.context )
        return oid, self.resolver_id

