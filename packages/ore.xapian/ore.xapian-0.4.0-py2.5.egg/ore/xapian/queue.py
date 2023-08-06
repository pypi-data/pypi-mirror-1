"""
$Id: $
"""

import Queue, threading, transaction

# we do async indexing with all indexing operations put into this queue
index_queue = Queue.Queue()


# async queue processor
class QueueProcessor( object ):

    # Flush every _n_ changes to the db
    FLUSH_THRESHOLD = 20

    # Poll every _n_ seconds for changes
    POLL_TIMEOUT = 60

    indexer_running = False
    indexer_thread = None

    def __init__( self, connection ):
        self.connection = connection 

    def operations( self ):
        # iterator never ends, just sleeps when no results to process
        while self.indexer_running:
            # get an operation in blocking fashion
            try:
                op = index_queue.get(True, self.POLL_TIMEOUT )
            except Queue.Empty:
                yield None
            else:
                yield op
                

    def __call__( self ):
        # number of documents indexed since last flush
        op_delta = 0

        # loop through queue iteration
        for op in self.operations():

            # on timeout the op is none
            if op is None:
                # if we indexed anything since the last flush, flush it now
                if op_delta:
                    self.connection.flush()
                    op_delta = 0
                continue
            # process the operation
            op.process( self.connection )
            op_delta += 1
            
            if op_delta % self.FLUSH_THRESHOLD == 0:
                self.connection.flush()
                op_delta = 0
            
    @classmethod
    def start( klass, connection ):
        if klass.indexer_running:
            raise SyntaxError("Indexer already running")
        
        klass.indexer_running = True
        indexer = klass( connection )
        klass.indexer_thread = threading.Thread(target=indexer)
        klass.indexer_thread.setDaemon(True)
        klass.indexer_thread.start()
        return indexer

    @classmethod
    def stop( klass ):
        if not klass.indexer_running:
            return

        klass.indexer_running = False
        klass.indexer_thread.join()
    
