"""
$Id: $
"""

from sqlalchemy import orm
from zope.dottedname.resolve import resolve

# utility functions        
def getKeyAndTable( ob ):
    mapper = orm.object_mapper( ob )
    primary_key = mapper.primary_key_from_instance( ob )
    return primary_key, mapper.select_table.fullname

def getClassName( ob ):
    klass = object.__class__
    return "%s.%s"%( klass.__module__, klass.__name__ )

class AlchemistResolver( object ):
    """
    resolver for sqlalchemy mapped objects
    """

    def id( self, object ):
        pass

    def resolve( self, id ):
        pass

class SubversionResolver( object ):
    """
    resolver for subversion nodes ( ore.svn )
    """
    
    def id( self, object ):
        pass

    def resolve( self, id ):
        pass
