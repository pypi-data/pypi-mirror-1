####################################################################
# Copyright (c) Kapil Thangavelu <kapil.foss@gmail.com. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
####################################################################

"""
$Id: $
"""

from zope import component, interface

import transaction
import threading
import xappy
import interfaces
import queue
import logging

log = logging.getLogger('ore.xapian')

class IndexOperation( object ):
    """
    an async/queued index operation
    """

    interface.implements( interfaces.IIndexOperation )

    __slots__ = ('oid', 'resolver_id', 'requeue')
    requeue = False
    
    def __init__( self, oid, resolver_id ):
        self.oid = oid
        self.resolver_id = resolver_id

    def resolve( self ):
        if self.resolver_id:
            resolver = component.getUtility( interfaces.IResolver , self.resolver_id ) 
        else:
            resolver = component.getUtility( interfaces.IResolver )
        instance = resolver.resolve( self.oid )

        if not instance:
            log.error("Idx Operation - Could Not Resolve %s"%(self.oid))
            return
#            return interfaces.OP_REQUEUE
        
        return instance

    def process( self, connection ):
        raise NotImplemented

    @property
    def document_id( self ):
        return self.oid

class AddOperation( IndexOperation ):
    
    interface.implements( interfaces.IAddOperation )

    def process( self, connection ):
        if interfaces.DEBUG_LOG: log.info("Adding %r"%self.document_id )
        instance = self.resolve()
#        if not instance or instance == interfaces.OP_REQUEUE:
#            return instance
        doc = interfaces.IIndexer( instance ).document( connection )
        doc.id = self.document_id
        doc.fields.append( xappy.Field('resolver', self.resolver_id or '' ) )
        connection.add( doc )
        
class ModifyOperation( IndexOperation ):

    interface.implements( interfaces.IModifyOperation )
    
    def process( self, connection ):
        if interfaces.DEBUG_LOG: log.info("Modifying %r"%self.document_id )        
        instance = self.resolve()
#        if not instance or instance == interfaces.OP_REQUEUE:
#            return instance        
        doc = interfaces.IIndexer( instance ).document( connection )
        doc.id = self.document_id        
        doc.fields.append( xappy.Field('resolver', self.resolver_id ) )
        connection.replace( doc )
    
class DeleteOperation( IndexOperation ):

    interface.implements( interfaces.IDeleteOperation )
    
    def process( self, connection ):
        if interfaces.DEBUG_LOG: log.info("Deleting %r"%self.document_id )                
        connection.delete( self.document_id )

class OperationBufferManager( object ):
    """
    ideally we'd be doing this via the synchronizer api, but that has several
    issues, which i need to work on in the transaction package, for now the
    standard transaction manager api suffices.
    """
    
    def __init__( self, buffer):
        self.buffer = buffer

    def tpc_finish( self, transaction ):
        self.buffer.flush()
        
    def abort( self, transaction):
        self.buffer.clear()

    def sortKey( self ):
        return str(id(self))

    def commit( self, transaction ):
        pass

    tpc_abort = abort
    tpc_vote = tpc_begin = commit


class OperationBuffer( object ):
    """
    an operation buffer aggregates operations across a transaction
    """

    def __init__( self ):
        self.ops = {}
        self.registered = False

    def add( self, op ):
        """add an operation to the buffer, aggregating with existing operations"""
        previous = self.ops.get( op.document_id )
        if previous is not None:
            op = self._choose( previous, op)
        if op is not None:
            self.ops[ op.document_id ] = op
        if not self.registered:
            self._register()

    def clear( self ):
        self.ops = {}
        self.registered = False
        self.manager = None
        
    def flush( self ):
        for op in self.ops.values():
            queue.index_queue.put( op )
        self.ops = {}
        self.registered = False
        self.manager = None
            
    def _register( self ):
        self.manager = OperationBufferManager( self )    
        self.registered = True
        transaction.get().join( self.manager )

    def _choose( self, previous, new ):
        """
        for a given content object, choose one operation to perform given
        two candidates. can also return no operations.
        """
        p_kind = (interfaces.IDeleteOperation.providedBy( previous ) and 2) \
                 or (interfaces.IAddOperation.providedBy( previous ) and 1) \
                 or (interfaces.IModifyOperation.providedBy( previous ) and 0)
                 
        n_kind = (interfaces.IDeleteOperation.providedBy( new ) and 2) \
                 or (interfaces.IAddOperation.providedBy( new ) and 1) \
                 or (interfaces.IModifyOperation.providedBy( new ) and 0)

        # if we have an add and then a delete, its an effective no-op
        if ( p_kind == 1 and n_kind == 2 ):
            return None
        if p_kind > n_kind:
            return previous
        return new

_buffer = threading.local()

def get_buffer( ):
    op_buffer = getattr( _buffer, 'buffer', None)
    if op_buffer is not None:
        return op_buffer
    op_buffer = OperationBuffer()
    _buffer.buffer = op_buffer
    return op_buffer
    

class OperationFactory( object ):

    interface.implements( interfaces.IOperationFactory )

    __slots__ = ('context',)

    resolver_id = '' # default resolver

    def __init__( self, context ):
        self.context = context
    
    def add( self ):
        return self._store( AddOperation( *self._id() ) )

    def modify( self ):
        return self._store( ModifyOperation( *self._id() ) )

    def remove( self ):
        return self._store( DeleteOperation( *self._id() ) )
        
    def _store( self, op ):

        # optionally enable synchronous operation, which bypasses the queue, for testing
        # purposes.
        if interfaces.DEBUG_SYNC and interfaces.DEBUG_SYNC_IDX:
            if interfaces.DEBUG_LOG: log.info("Processing %r %r"%(op.oid, op) )
            op.process( interfaces.DEBUG_SYNC_IDX )
            interfaces.DEBUG_SYNC_IDX.flush()
            if interfaces.DEBUG_LOG: log.info("Flushed Index")            
        else:
            get_buffer().add( op )
        
    def _id( self ):
        if self.resolver_id:
            resolver = component.getUtility( interfaces.IResolver , self.resolver_id ) 
        else:
            resolver = component.getUtility( interfaces.IResolver )
        oid = resolver.id( self.context )
        if not oid:
            raise KeyError( "Key Not Found %r"%( self.context ) )
        return oid, self.resolver_id

