# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:et:sw=4:ts=4

from __future__ import ( generators, with_statement )
from commons import log
from commons.threads import synchronized
from Queue import Queue
from threading import Lock, Thread, currentThread
import socket
from functools import partial, wraps
from contextlib import closing
from os import environ
from sys import exc_info
from cProfile import runctx

import af

from .pubsub import stop as stop_msg

__all__ = [ 'block',
            'call_from_thread',
            'call_in_thread',
            'task',
            'unblock', ]

debug = partial( log.debug, __name__ )
info  = partial( log.info, __name__ )
error = partial( log.error, __name__ )

itc_port = 17777 if 'ITC_PORT' not in environ \
           else int( environ[ 'ITC_PORT' ] )

p = None

class pool( object ):

    def __init__( self, size = 5 ):
        self.i = Queue()
        self.o = Queue()
        self.size = size
        self.port = itc_port
        self.threads = None
        self.s = None
        self.stopped = False
        self.lock = Lock()

    def start( self ):
        if self.stopped: return

        i = self.i
        o = self.o

        with closing( socket.socket() ) as l:
            l.setsockopt( socket.SOL_SOCKET,
                          socket.SO_REUSEADDR, 1 )
            l.bind( ( 'localhost', self.port ) )
            l.listen(1)
            l.settimeout(1)
            debug( 'pool listening' )
            s = None
            while s is None:
                with self.lock:
                    if self.stopped: return
                try: s,_ = l.accept()
                except socket.timeout: pass
            
        debug( 'pool accepted' )

        def worker():
            def real_worker():
                debug( 'starting worker' )
                while True:
                    msg = i.get()
                    if msg is stop_msg: break
                    resultbuf, func, args, kwargs = msg
                    result, exc = None, None
                    try:
                        result = func( *args, **kwargs )
                    except:
                        t, v, tb = exc_info()
                        exc = t, v, tb.tb_next
                    o.put( ( resultbuf, result, exc ) )
                    s.send( 'x' ) # assuming socket.send is thread-safe
                debug( 'stopping worker' )
            if environ.get( 'PYPROF', '' ) != '':
                try: outpath = environ['PYPROF'] % currentThread().getName()
                except: real_worker()
                else: runctx( 'real_worker()', locals(), globals(), outpath )
            else:
                real_worker()

        with self.lock:
            if not self.stopped:
                self.s = s
                self.threads = [ Thread( target = worker ).start()
                                 for _ in xrange( self.size ) ]
            else:
                s.close()

    def stop( self ):
        with self.lock:
            if self.threads is not None:
                [ self.i.put( stop_msg )
                  for _ in xrange( len( self.threads ) ) ]
            if self.s is not None: self.s.close()
            self.stopped = True

def start_thread_pool():
    global i,o,p,q
    p = pool()
    i, o = p.i, p.o
    q = Queue()
    Thread( target = p.start ).start()

@af.task
def waker():
    debug = partial( log.debug, __name__ + '.waker' )
    try:
        debug( 'waker starting' )
        s = None
        while True:
            try:
                s = pool.s = yield af.socket.connect( 'localhost', itc_port, type = socket.SOCK_STREAM )
            except af.cancelled:
                raise
            except:
                yield af.timeout(.5)
                debug( 'retrying', itc_port )
            else:
                break
        debug( 'waker connected' )
        while True:
            xs = yield s.read_some(4096)
            if len( xs ) == 0:
                break
            for x in xs:
                resultbuf, result, exc = o.get()
                yield resultbuf.put( ( result, exc ) )
    except af.cancelled:
        debug( 'cancelled!' )
        stop_thread_pool()
        raise

def stop_thread_pool():
    if p is not None: p.stop()

@af.task
def call_in_thread( func, *args, **kwargs ):
    """
    Inspired by Twisted's C{callInThread}.
    """
    global i
    resultbuf = af.channel(1)
    i.put( ( resultbuf, func, args, kwargs ) )
    result, exc = yield resultbuf.get()
    if exc is not None:
        t, v, tb = exc
        raise t, v, tb
    yield af.result( result )

class block( object ): pass
class unblock( object ): pass

def task( f ):
    """
    Inspired by
    U{http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440670}.
    """
    @af.task
    @wraps( f )
    def wrapper( *args, **kwargs ):
        coro = f( *args, **kwargs )
        item = coro.next()
        while True:
            if type( item ) is block:
                result = yield call_in_thread( coro.send, item )
                assert type(result) is unblock, 'type(result) = %s' % type(result)
            else:
                result = yield item
            item = coro.send( result )
    return wrapper

@af.task
def watcher():
    global q
    while True:
        task, args, kwargs = yield call_in_thread( lambda: q.get() )
        af.spawn( task( *args, **kwargs ) )

def call_from_thread( task, *args, **kwargs ):
    global q
    q.put( ( task, args, kwargs ) )
