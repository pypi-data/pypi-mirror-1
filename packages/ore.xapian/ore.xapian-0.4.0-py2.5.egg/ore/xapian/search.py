"""
$Id: $
"""

from zope import component, interface
from threading import local

import time
import thread
import xappy
import interfaces

class ConnectionHub( object ):
    """
    search connection storage and retrieval with automatic
    reconnections with connection aging, connections are
    all thread local.
    """
    
    auto_refresh_delta = 20 # max time in seconds till we refresh a connection
    # 
    def __init__( self, index_path ):
        self.store = local()
        self.modified = time.time()
        self.index_path = index_path
        
    def invalidate( self ):
        self.modified = time.time()

    def get( self ):
        conn = getattr( self.store, 'connection', None)
        
        now = time.time()
        if self.modified + self.auto_refresh_delta < now:
            self.modified = now
        
        if conn is None:
            self.store.connection = conn = xappy.SearchConnection( self.index_path )
            self.store.opened = now
                
        opened = getattr( self.store, 'opened' )
        
        if opened < self.modified:
            conn.reopen()            
            self.store.opened = now
            
        return conn
        
class IndexSearch( object ):

    interface.implements( interfaces.IIndexSearch )
    
    def __init__( self, index_path ):
        self._index_path = index_path
        self.hub = ConnectionHub( index_path )
        
    def __call__( self ):
        return self.hub.get()

    def invalidate( self ):
        self.hub.invalidate()

def object( self ):
    resolver_id = self.data['resolver'][0]
    resolver = component.getUtility( interfaces.IResolver, resolver_id )
    return resolver.resolve( self.id )

# rather than rewrapping results one by one, and increasing memory usage, just attach
# a resolving method onto search results.
xappy.searchconnection.SearchResult.object = object
