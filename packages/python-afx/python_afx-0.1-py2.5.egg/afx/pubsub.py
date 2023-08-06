# -*- mode: python; tab-width: 2; indent-tabs-mode: nil; py-indent-offset: 2; -*-
# vim:et:sw=4:ts=4

# TODO rename something to 'skip channels' (a la ch paper)

from __future__ import ( generators, with_statement )
from contextlib import closing
from cStringIO import StringIO
from itertools import chain
from struct import unpack
from cPickle import load
from commons.log import warning
from commons.seqs import streamlen, safe_pickler
import af

stop = 'stop'

class publisher( object ):
    """
    Publish-subscribe mechanism. Subscribers are just channels.

    If L{just_once} is L{True}, then at most one item at a time will be put in
    any subscription channel.
    """
    def __init__( self, just_once = False ):
        self.outs = []
        self.just_once = just_once
    def register( self, listener ):
        self.outs.append( listener )
    @af.task
    def publish( self, item ):
        #from commons.log import warning
        #print 'PUSHING TO', len(self.outs)
        #warning( '', 'PUSHING TO', len(self.outs) )
        for out in self.outs:
            #print 'PUSH?', self.just_once, len(out._queue)
            #warning( '', 'PUSH?', self.just_once, len(out._queue) )
            if not self.just_once or len( out._queue ) == 0:
                #print 'PUSH!'
                #warning( '', 'PUSH!' )
                yield out.put( item )

#### class subscriber( object ):
####     @af.task
####     def put( self, item ):
####         yield self.out.put( item )

class condvar( object ):
    """
    Condition variable.
    """
    def __init__( self, token = None ):
        self.waiters = []
        self.token = token
    @af.task
    def wait( self, result = None ):
        c = af.channel( 1 )
        self.waiters.append( c )
        yield c.get()
        yield af.result( result )
    def notify_one( self ):
        if len( self.waiters ) > 0:
            res = self.waiters.pop().try_put( self.token )
            assert res
    def notify( self ):
        res = [ w.try_put( self.token ) for w in self.waiters ]
        assert all( res )
        self.waiters = []

class bool( object ):
    """
    A bool on which threads can wait for notifications about changes in state.
    """
    def __init__( self, value = False ):
        self.onset = condvar()
        self.onreset = condvar()
        self.value = value
        self.renotify = False
    # TODO change for py 2.6/py 3
    def __nonzero__( self ):
        return self.value
    def set( self ):
        if not self.value or self.renotify:
            self.value = True
            self.onset.notify()
    def reset( self ):
        if self.value or self.renotify:
            self.value = False
            self.onreset.notify()
    @af.task
    def waitset( self, result = None ):
        while not self.value: yield self.onset.wait()
        yield af.result( result )
    @af.task
    def waitreset( self, result = None ):
        while self.value: yield self.onreset.wait()
        yield af.result( result )

def deplete_iter( ch ):
    """
    Generator that yields elements in the channel until it is empty.
    """
    while True:
        rem, res = ch.try_get()
        if not rem: break
        yield res

def deplete( ch ):
    """
    Return a list of all the remaining elements in the channel until it is
    empty.
    """
    return list( deplete_iter( ch ) )

def size( ch ):
    """
    Get the size of a channel.
    """
    return ch._queue_max

def remaining( ch ):
    """
    Get the remaining capacity of the channel.
    """
    return ch._queue_max - len( ch._queue )

@af.task
def get_all( ch ):
    """
    I will return all items from this channel, blocking until I have at least
    one item to return.
    """
    item = yield ch.get()
    yield af.result( chain( [ item ], deplete_iter( ch ) ) )

class wfq( object ):
    """
    I'm a simple prioritized fair queue. I'm like a regular channel, except that
    when users L{get} from me, I return the min item.

    @todo: rename this
    """
    def __init__( self, n = 0, *args, **kwargs ):
        """
        Initializer.

        @param n: maximum size of this queue, or None for infinite
        @type n: int

        @param args: extra args to pass into the L{structs.Heap}

        @param kwargs: extra kwargs to pass 
        """
        self.q = af.channel( n )
        self.xs = structs.Heap( *args, **kwargs )
    @af.task
    def put( self, x ):
        self.xs.push( x )
        yield self.q.put( x )
    @af.task
    def get( self ):
        yield self.q.get()
        yield af.result( self.xs.popmin() )

class fq( object ):
    """
    I'm a simple round-robin fair queue. I'm like a regular channel, except
    that when users L{put} an element into me, the element is associated with a
    key (which represents an "input source"). When user later L{get} from me, I
    pick elements from each of my keys in round-robin fashion, in the order in
    which they were inserted. This way, each input source effectively gets its
    own queue, and I can dequeue from the multiple input sources fairly.

    q = fq( 10 )
    yield q.put('user 1', 'packet 1')
    yield q.put('user 1', 'packet 2')
    yield q.put('user 1', 'packet 3')
    yield q.put('user 2', 'packet 4')
    yield q.put('user 2', 'packet 5')
    yield q.put('user 2', 'packet 6')
    while True:
        packet = yield q.get()
        yield send( packet ) # send packets 1, 4, 2, 5, 3, 6
    """
    def __init__( self, n = 0 ):
        """
        Initializer.

        @param n: maximum size of this queue, or None for infinite
        @type n: int
        """
        self.n = n
        self.qs = {}
        self.keys = []
        self.incoming = condvar()
    def _getq( self, k ): 
        try: q = self.qs[ k ]
        except KeyError: q = self.qs[ k ] = af.channel( self.n )
        return q
    @af.task
    def put( self, k, x ):
        q = self._getq( k )
        self.incoming.notify_one()
        yield q.put( x )
    @af.task
    def get( self ):
        while True:
            for k in self.keys:
                avail, x = self.qs[ k ].try_get()
                if avail:
                    yield af.result( ( k, x ) )
                else:
                    # garbage-collect
                    del self.qs[ k ]
            else:
                if len( self.qs ) == 0:
                    yield self.incoming.wait()
####                # garbage-collection
####                for k in self.qs.keys():
####                    if k not in self.qs:
####                        del self.qs[ k ]
                self.keys = iter( self.qs.keys() )

# TODO can the following be done without learning about dispatchables?

#class fm( object ):
#    """
#    Round-robin fair multiplexor.
#    """
#    def __init__( self, resource ):
#        self.fq = fq()
#        self.resource = resource
#        af.spawn( self.start )
#    @af.task
#    def start( self ):
#        while True:
#            yield self.fq.get()
#    @af.task
#    def slot( self, k ):
#        yield self.fq.put( k, 0 )
#        parent = self
#        class fmhelper( object ):
#            def __enter__( self ):
#                parent.fq._getq( k ).try_put( 0 )
#                return parent.resource
#            def __exit__( self, *args ): pass
#####        self.resource = resource
#        yield af.result( fmhelper() )

def is_disp( proc ):
    return isinstance( proc, af._task._dispatchable )

def is_task( proc ):
    return isinstance( proc, af.task )

# XXX this won't work with exceptions
# XXX huh? what do i mean by the above?
#@af.task
#def tagged_any( tasks* ):
#    yield any( tag( task, index ) for index, task in enumerate( tasks ) )

@af.task
def tag( task, attach ):
    result = yield task
    yield af.result( ( attach, result ) )

class cell( object ):
    """
    Holds a single value, and replaces it on each put.
    Puts are also non-yielding.
    """
    def __init__( self ):
        self.q = af.channel( 1 )
    def put( self, x ):
        deplete( self.q )
        res = self.q.try_put( x )
        assert res
    @af.task
    def get( self ):
        yield af.result( ( yield self.q.get() ) )

@af.task
def read_pickle( read, init = '', length_thresh = 100000 ):
    with closing( StringIO() ) as sio:
        obj = None # return this if we hit eof (not enough bytes read)
        sio.write( init )

        @af.task
        def read_until(target):
            remain = target - streamlen(sio)
            if remain > 0:
                chunk = yield read( remain )
                # append to end
                sio.seek(0,2)
                sio.write( chunk )
            offset = streamlen(sio)
            sio.seek(0)
            yield af.result( offset >= target )

        if ( yield read_until(4) ):
            lengthstr = sio.read(4)
            (length,) = unpack('i4', lengthstr)
            if length_thresh is not None and length > length_thresh or \
                    length <= 0:
                warning( 'read_pickle',
                         'got length', length,
                         'streamlen', streamlen(sio),
                         'first bytes %x %x %x %x' % tuple(map(ord,lengthstr)) )
            if ( yield read_until(length + 4) ):
                # start reading from right after header
                sio.seek(4)
                obj = load(sio)

        yield af.result( ( obj, sio.read() ) )

####        stream.write( init )
####        while True:
####            try:
####                stream.seek( 0 )
####                obj = load( stream )
####                if len( chunk ) == 0:
####                    yield af.result( ( None, stream.getvalue() ) )
####                stream.write( chunk )
####            else:
####                yield af.result( ( obj, stream.read() ) )

class socket_unpickler( object ):
    """
    Pickle objects directly to a socket stream.
    """

    def __init__( self, s ):
        self.s = s
        self.buffer = ''

    @af.task
    def read( self ):
        obj, self.buffer = yield read_pickle( self.s.read, self.buffer )
        yield af.result( obj )



class socket_line_reader( object ):
    """
    A line-reading interface to socket streams.
    """
    def __init__( self, s ):
        self.s = s
        self.buffer = []

    @af.task
    def read_line( self ):
        """
        Hopefully more performant than af._handle._handle.read_line(),
        and can read unlimited size strings.
        """
        while True:
            chunk = yield self.s.read_some()
            if len( chunk ) == 0: break
            start = 0
            while True:
                end = chunk.find( '\n', start )
                if end > 0:
                    line = ''.join( chain( self.buffer,
                                           [ chunk[ start : end ] ] ) )
                    self.buffer = [ chunk[ end + 1 : ] ]
                    yield af.result( line )
                else:
                    self.buffer.append( chunk[ start : ] )

    @af.task
    def read_some_lines( self ):
        """
        Reads several lines at a time, yielding until at least one line can be
        read, or the EOF is encountered. If there are no lines, returns the
        empty string.
        """
        while True:
            # read_some returns '' if eof
            chunk = yield self.s.read_some()
            end = chunk.rfind( '\n' )
            if end >= 0 or chunk == '':
                line = ''.join( chain( self.buffer,
                                       [ chunk[ : end + 1 ] ] ) )
                self.buffer = [ chunk[ end + 1 : ] ]
                yield af.result( line )
            else:
                self.buffer.append( chunk )



@af.task
def get_traceback():
    import sys
    try: raise Exception()
    except: yield af.result( sys.exc_info()[2] )

@af.task
def get_tb_string():
    import traceback
    tb = yield get_traceback()
    yield af.result( '\n'.join( traceback.format_tb( tb ) ) )

