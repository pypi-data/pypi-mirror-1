----------
ore.xapian
----------

The package provides a content indexing framework for a multi-threaded
python application. It utilizes xapian for its indexing library, and the
zope component architecture for flexibility. It operates primarily as a
framework wrapper for xapian core search facilities.

features 

 - processes all indexing operations asynchronously.

 - mechanisms for indexing/resolving content from multiple data stores.

 - easy to customize indexing behavior via adaptation.

 - transaction aware modifications, aggregates operations for content
   within a transaaction scope.

Content
-------

Let's create some content to work with. The only responsibility on
content for purposes of integration with indexing is that they
implement the IIndexable marker interface. 

  >>> class Content( object ):
  ...    implements( interfaces.IIndexable )
  ...    __parent__ = None
  ...    @property
  ...    def __name__( self ): return self.title
  ...    def __init__( self, **kw): self.__dict__.update(kw)
  ...    def __hash__( self ): return hash(self.title)
  >>>
  >>> rabbit = Content( title=u"rabbit", description="furry little creatures")
  >>> elephant = Content( title=u"elephant", description="large mammals with memory")
  >>> snake = Content( title=u"snake", description="reptile with scales")   
  >>>

Resolvers
---------

Resolvers allow us to index content from multiple data stores. ie. we
could have content from a relational database, and content from a
subversion, and content from the fs, that we'd like to index into
xapian. Resolvers allow us to unambigously identify object via an
identifier, and to retrieve an object given its identifier. Resolvers
are structured as named utilities, with the utility name corresponding
to the resolving strategy. 

One key requirement, is that we need to be able to load the content
asynchronously in a different thread in order for the indexing
machinery to work with it.

For the purposes of testing we'll construct a simple resolver scheme
and some sample content here:

  >>> class ContentResolver( object ):
  ...    implements( interfaces.IResolver )
  ...    scheme = "" # name of resolver utility ( optionally "" for default )
  ...    map = dict( rabbit=rabbit, elephant=elephant, snake=snake )
  ...
  ...    def id( self, object ): return object.title
  ...    def resolve( self, id ): return self.map[id]
  ...
  >>> component.provideUtility( ContentResolver() )

Catalog Definition
------------------

a core responsibility of any application utilizing this package, is to
define the application specific fields of interest to index. 

an application does this via constructing a xapian index connection
and adding additional fields:

  >>> import xappy
  >>> indexer = xappy.IndexerConnection('tmp.idx')
  >>> indexer.add_field_action('resolver', xappy.FieldActions.INDEX_EXACT )
  >>> indexer.add_field_action('resolver', xappy.FieldActions.STORE_CONTENT )
  >>> indexer.add_field_action('title', xappy.FieldActions.INDEX_FREETEXT )
  >>> indexer.add_field_action('title', xappy.FieldActions.STORE_CONTENT )
  >>> indexer.add_field_action('description', xappy.FieldActions.INDEX_FREETEXT )


Queue Processor
---------------

Now we can startup our asynchronous indexing thread, with this
index connection. Note we shouldn't attempt to perform any indexing
directly in the application threads with this indexer, as no locking is
performed by xapian. Instead, write operations are routed to the queue
processor which performs all modifications to the index in a separate
thread/process. For the purposes of testing, we'll also lower the time
threshold for index flushes (default 60s):

For test purposes, we set the poll timeout to 0.1 seconds.

  >>> from ore.xapian import queue
  >>> queue.QueueProcessor.POLL_TIMEOUT = 0.1
  >>> queue.QueueProcessor.FLUSH_THRESHOLD = 1  

Let's start the indexing queue. We typically do this in ZCML, but its not 
required, and for testing purposes we'll do it directly from python.

  >>> queue.QueueProcessor.start( indexer )
  <ore.xapian.queue.QueueProcessor object at ...>

Verify that the queue is running.
  
  >>> queue.QueueProcessor.indexer_running
  True

Indexing
--------

Content indexing is automatically provided via event integration. Event 
subscribers for object modified, object added, and object removed are
utilized to generate index operations which are processed asynchronously 
by the queue processor. 

Operations
==========

However in order for the proper resolver to be associated with the
index operations for each object we need to construct an operation
factory thats associated to the resolver. The appropriate operation 
factory for an object will be found via adaptation:

  >>> from ore.xapian.operation import OperationFactory
  >>> class MyOperationFactory( OperationFactory ):
  ...      resolver_id = ContentResolver.scheme
  >>> component.provideAdapter( MyOperationFactory, (interfaces.IIndexable,) )

The operation factory is used by the various event handlers to create
operations for the index queue. The default implementation already
provides an appropriate generic implementation for the creation of
operations, our customization is only to ensure that the factory uses
the specified resolver.

Content Integration
===================

Applications will be typically be indexing many types of objects
corresponding to different interfaces and with different attribute
values. An index however tries to index object attributes into a
common set of fields appropriate for generic application usage and 
search interfaces. Therefore a common application need is to customize
the representation of an object that is indexed. 

  >>> class ContentIndexer( object ):
  ...      implements( interfaces.IIndexer )
  ...      def __init__( self, context): self.ob = context
  ...      def document( self, connection ):
  ...          doc = xappy.UnprocessedDocument()
  ...          doc.fields.append( xappy.Field( 'title', self.ob.title ))
  ...          doc.fields.append( xappy.Field( 'description', self.ob.description ))
  ...          return doc  
  >>> 
  >>> component.provideAdapter( ContentIndexer, (interfaces.IIndexable,) ) 

Now let's generate some events to kickstart the indexing:
   
  >>> from zope.event import notify
  >>> from zope.app.container.contained import ObjectAddedEvent
  >>>
  >>> notify( ObjectAddedEvent( rabbit ) )
  >>> notify( ObjectAddedEvent( elephant ) )
  >>> notify( ObjectAddedEvent( snake ) )

In order to have the indexer process these events, we need to commit the
transaction.

  >>> transaction.commit()
  >>> import time
  >>> time.sleep(0.1)  

Searching
--------- 

Search Utilities are analagous to xapian search connections. To allow
for reuse of a connection and avoid passing constructor arguments, 
we construct a search gateway which functions as a container for 
pooling search connections and which we register as a utility for
easy access:
 
  >>> from ore.xapian import search
  >>> search_connections = search.ConnectionHub('tmp.idx')

We can get a search connection from a gateway by calling it:

  >>> searcher = search_connections.get()
  >>> query = searcher.query_parse('rabbit')
  >>> results = searcher.search( query, 0, 30)
  >>> len(results)
  1
  
We can retrieve the object indexed by calling the object() method on 
a individual search result:

  >>> results[0].object() is rabbit
  True
 
  >>> query = searcher.query_parse('mammals')
  >>> results = searcher.search( query, 0, 30 )
  >>> len(results) == 1
  True

Content Integration Redux
-------------------------

For verification let's test modification and deletion as well.

  >>> from zope.lifecycleevent import ObjectModifiedEvent
  >>> from zope.app.container.contained import ObjectRemovedEvent

We'll give the rabbit a new description.
  
  >>> rabbit.description = 'hairy little animal'
  >>> notify(ObjectModifiedEvent(rabbit))

And delete the snake-object.

  >>> notify(ObjectRemovedEvent(snake))

Wait a bit and reopen the search connection.

  >>> transaction.commit()
  >>> time.sleep(0.1)  
  >>> searcher.reopen()
  
Verify search results:

  >>> query = searcher.query_parse('hairy')
  >>> len(searcher.search(query, 0, 30))
  1

  >>> query = searcher.query_parse('snake')
  >>> len(searcher.search(query, 0, 30))
  0
  
Cleanup
-------

To be a good testing citizen, we cleanup our queue processing thread.
  
  >>> queue.QueueProcessor.stop()

Caveats
-------

There are several caveats to using an indexing against relational
content, the primary one of concern is the use of non index aware
applications, performing modifications of the database structure.

there are additional ways to deal with this, if the index queue
is moved directly into the database, then modifying applications
can insert operations directly into the index queue. additionally
most databases support trigger operations that can perform this
functionality directly in the schema structure.

the additional constraint with using database based operations is
that additional properties of the domain model may be lost, or 
hard to capture for other appliacations or database triggers.

