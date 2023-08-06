from zope.interface import Interface
from zope.configuration.fields import GlobalObject

from ore.xapian import MessageFactory as _
from ore.xapian import queue

class IQueueDirective(Interface):
    indexer = GlobalObject(
        title=_("Xapian indexer"),
        required=True)

def queueDirective(_context, indexer):
    # start the processing thread
    queue.QueueProcessor.start(indexer)

    
    

