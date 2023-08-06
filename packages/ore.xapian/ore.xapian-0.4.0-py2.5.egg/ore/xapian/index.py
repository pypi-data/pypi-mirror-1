
import xappy
from zope import interface, schema

import interfaces

# content indexer
class DefaultContentIndexer( object ):
    
    interface.implements( interfaces.IIndexer )
    
    def __init__( self, context ):
        self.context = context

    def document( self, connection ):
        """
        return a xapian index document from the context.

        we can introspect the connection to discover relevant fields available.
        """
        doc = xappy.UnprocessedDocument()        
        for iface in interface.providedBy( self.context ):
            for field in schema.getFields( iface ).values():
                if not isinstance( field, ( schema.Text, schema.ASCII ) ):
                    continue
                value = field.query( self.context )
                if value is None:
                    value = u''
                if not isinstance( value, (str, unicode)):
                    value = unicode( value )
                doc.fields.append(  xappy.Field(field.__name__, value ) )
        return doc
        
