"""
$Id: $
"""

from zope import interface, schema

OP_ADDED = 'added'
OP_DELETED = 'deleted'
OP_MODIFED = 'modified'

class IIndexable( interface.Interface ):
    """
    marker interface for content to be indexed
    """

class IIndexer( interface.Interface ):
    """
    indexes an object into the index
    """

    def index( connection ):
        """
        index an object into the connection
        """

class IIndexOperation( interface.Interface ):

    oid = schema.ASCIILine( description=u"The identifier for the content" )
    
    resolver_id = schema.ASCIILine( description=u"The resolver used to find the content" )
    
    def process( connection ):
        """
        process an index operation
        """

class IDeleteOperation( IIndexOperation ): pass
class IModifyOperation( IIndexOperation ): pass
class IAddOperation( IIndexOperation ): pass        

class IOperationFactory( interface.Interface ):
    """
    creates operations, customizable by context, useful for creating classes
    of indexers across an entire class of objects (rdb, svn, fs, etc).
    """

    def add( ):
        """
        create an add operation
        """

    def modify( ):
        """
        create a modify operation
        """

    def delete( ):
        """
        create a delete operation
        """

class IResolver( interface.Interface ):
    """
    provides for getting an object identity and resolving an object by
    that identity. these identities are resolver specific, in order
    to resolve them from a document, we need to store the resolver name
    with the document in order to retrieve the appropriate resolver.
    """
    
    scheme = schema.TextLine(title=u"Resolver Scheme",
                             description=u"Name of Resolver Utility")

    def id( object ):
        """
        return the document id represented by the object
        """
        
    def resolve( document_id ):
        """
        return the object represented by a document id
        """

class IIndexConnection( interface.Interface ):
    """
    a xapian index connection
    """

class ISearchConnection( interface.Interface ):
    """
    a xapian search connection
    """

class IIndexSearch( interface.Interface ):
    """
    an access mediator to search connections, to allow for better reuse
    of search connections, avoid the need to carry constructor parameters
    when getting a search connection, and for the framework to provide
    for automatic reopening of connections when the index is modified.
    """

    def __call__( ):
        """
        return a search connection
        """
