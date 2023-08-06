# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:et:sw=4:ts=4

from __future__ import ( generators, with_statement )
from contextlib import contextmanager
import af

__all__ = [ 'server', 'pool' ]

class server( object ):
    def __init__( self, host, port ):
        self.s = af.socket.socket()
        self.s.bind( ( host, port ) )
        self.s.listen()
    def __enter__( self ): return self
    def __exit__( self, *args ): self.s.close()
    @af.task
    def accept( self ):
        res = yield self.s.accept()
        yield af.result( res )
    def close( self ): self.s.close()

class pool( object ):
    def __init__( self, *tasks ):
        self.tasks = []
        self.spawn( *tasks )
    def spawn( self, *tasks ):
        self.tasks.extend( af.spawn( t ) for t in tasks )
    def __enter__( self ): return self
    def __exit__( self, *args ): self.stop()
    def stop( self ): [ task.stop() for task in self.tasks ]

@contextmanager
def stopping( x ):
    try: yield x
    finally: x.stop()
