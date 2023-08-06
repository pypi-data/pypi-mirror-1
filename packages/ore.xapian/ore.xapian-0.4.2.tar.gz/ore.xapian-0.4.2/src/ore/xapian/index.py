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
        
