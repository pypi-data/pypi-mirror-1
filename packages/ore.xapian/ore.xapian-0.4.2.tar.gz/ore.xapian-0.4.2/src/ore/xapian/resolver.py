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
