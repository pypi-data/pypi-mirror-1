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

from zope.interface import Interface
from zope.configuration.fields import GlobalObject

from ore.xapian import MessageFactory as _
from ore.xapian import queue

import interfaces

class IQueueDirective(Interface):
    indexer = GlobalObject(
        title=_("Xapian indexer"),
        required=True)

def queueDirective(_context, indexer):
    
    if interfaces.DEBUG_SYNC:
        return
    
    # start the processing thread

    queue.QueueProcessor.start(indexer, silent=True)

    
    

