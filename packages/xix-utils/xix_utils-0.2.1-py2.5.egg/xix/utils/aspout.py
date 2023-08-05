'''
utils.aspout allows outputting with an AOP twist.  To use this
module in your package, create a file in the package root, say
_io.py, create a dictionary mapping module names to ArbiterSequences,
and finally register each module name with this module's registry.
See _io.py in xix for a good example.

Some definitions (note, these are not class names!) to help understand this 
API:

1. Arbiter - acts a selector. The arbiter is the first check point for any 
output and decides whether or not to forward the output to the next stage in
the pipeline.

2. Pipeline - The Formatting pipeline, more correctly. This is
only a part of the whole pipeline and includes a sequence of
formatting rules to apply to the output.

3. Writer - The device.  The sink our process.  This is what actually _does_ 
the outputing via console writer, file log writing, notification via mail, 
whatever.

Now, the three basic stages of the utils.aspout pipeline should be
apparent.  Output goes to arbiter, arbiter forwards to formatting pipeline
and then to device (writer).  The unit of functionality, though, is the
ArbiterSequence, instances of which will be registered in the arbiters
registry.

What is an WriterAribiterSequence?  An object that simply acts as a list of 
Arbiters but is also callable.  This allows for different developers to plugin 
their own WriterArbiter.  For example, developer Bob want's an email when
"snafoo" appears in the output of module bar.py ... developer Sally wants an
html-log with messages formatted in <span> tags ... etc.

Copyright (c) 2005 Drew Smathers
See LICENSE for details.

'''

# $Id: aspout.py 159 2005-12-02 20:35:19Z drew $

#
# Note to developers.
# If you are extending this module with an external module,
# be sure to include the modules name in this module's
# namespace registry using the following call:
#
# registerInternalName(__name__)
# 

# TODO Add some usefull logging classes.

from zope.interface import Interface, Attribute, implements
from time import asctime
import inspect, sys
try:
    import thread
    import threading
except ImportError:
    import warning
    warning.warn('Failed importing threading modules!')
    thread = None

__author__ = 'Drew Smathers'
__copyright__ = '(c) 2005 Drew Smathers'
__revision__ = '$Revision: 159 $'
__license__ = 'MIT'

_io_internal_names = [ __name__ ] # append to this with registerInternalName

def registerInternalName( name ):
    '''Note that when registering a name, your module doing this should ONLY 
    an extension to this module. In other words, your module should not use 
    this module, as stack inspection, etc., will not work correctly if module's
    name is registered here. 
    '''
    _acquire_lock()
    try:
        if name not in _io_internal_names:
            _io_internal_names.append( name )
    finally:
        _release_lock()

def unregisterInternalName( name ):
    '''Unregister name name from list of internal names.
    '''
    # sanity check
    if name == __name__: return
    _acquire_lock()
    try:
        _io_internal_names.remove( name )
    finally:
        _release_lock()

#############################################################
# Simple lock for threading support.
# Provides serialized access to any internal data structures.
_lock = None
def _acquire_lock_functioning( ):
    global _lock
    _lock.acquire()
def _release_lock_functioning( ):
    global _lock
    _lock.release()
if thread:
    _lock = threading.RLock()
    _acquire_lock = _acquire_lock_functioning
    _release_lock = _release_lock_functioning
else:
    _acquire_lock = lambda : None
    _release_lock = lambda : None
# End lock setup
##############################################################


class Streams(object):
    ''' @todo testme
    '''
    stream_count = 7
    STDOUT, STDIN, STDERR, WARN, DEBUG, VERBOSE, SILLY = range(stream_count)
    # aliases:
    OUT, ERR = STDOUT, STDERR
    WARNING, DEBUGGING = WARN, DEBUG
    def add_stream(name):
        assert len(name) and name[0] != '_'
        self.__setattr__(name, self.stream_count)
        self.stream_count += 1
# Streams
streams = Streams()


###############################################################################
# Writer Arbiters. Writer Arbiters should 
# provide some logic optionally based on keywords passed to call

class IWriterAribiter(Interface):
    '''Decides whether or not to dispatch message to format pipeline
    and writer.
    '''

    pipelines = Attribute(
            '''List of formatting pipelines for arbiter to execute.
            ''')
    
    def arbite( message, stream=streams.STDOUT, *pargs, **kwargs ):
        '''Decide whether or not to output message.

        @param message: message for outputting
        @type  message: string
        @param  stream: stream to output on
        @type   stream: integer
        '''

    def __call__( message, stream, *pargs, **kwargs ):
        '''Executes arbite with given arguments 
        '''
        
# IWriterAribiter
    
class WriterArbiter:
    
    implements(IWriterAribiter)
    
    def __init__(self, pipelines=None):
        self.pipelines = pipelines or []
        self.write = self.arbite # alias
    def arbite(self, msg, stream=streams.OUT, *pargs, **kwargs):
        '''abstract
        '''
    def __call__(self, msg, stream=streams.OUT, *pargs, **kwargs):
        self.arbite(msg, *pargs, **kwargs)
# WriterArbiter

class StandardArbiter(WriterArbiter):
    
    def arbite(self, msg, stream=streams.OUT, *pargs, **kwargs):
        for pipeline in self.pipelines:
            pipeline.execute(msg, stream, *pargs, **kwargs)
# StandardArbiter


###############################################################################
# This is what the requesting module will get

class IWriterArbiterSequence ( Interface ):

    arbiters = Attribute(
            '''List of writer arbiters
            ''')

    def write( message, stream, *pargs, **kwargs ):
        '''Iterates over arbiters and calls arbite on each.
        '''

    def append( arbiter ):
        '''Adds an arbiter to the arbiter list.
        '''

    def remove( arbiter ):
        '''Removes arbiter from the arbiter list.
        '''
        
    def __call__( message, stream, *pargs, **kwargs ):
        '''Calls write with given arguments.
        '''
        
    def __iter__( self):
        '''Provides an iterator over the arbiters.
        '''

# IWriterArbiterSequence
    
    
class WriterArbiterSequence:

    implements( IWriterArbiterSequence )
    
    def __init__( self, arbiters=None ):
        self.arbiters = arbiters or []
        
    def write( self, msg, stream=streams.OUT, *pargs, **kwargs ):
        for arbiter in self.arbiters:
            arbiter.write(msg, stream=stream, *pargs, **kwargs)
    
    def append( self, arbiter ):
        self.arbiters.append(arbiter)
    
    def remove( self, arbiter ):
        self.arbiter.remove(arbiter)
    
    def __call__( self, msg, stream=streams.OUT, *pargs, **kwargs ):
        self.write(msg, stream=stream, *pargs, **kwargs)
    
    def __iter__( self ):
        return iter( self.arbiters )
    
    def _attach_streams(self):
        pass    
        
###############################################################################
# OutputPipelines
#

class IOutputPipeline(Interface):
    
    '''Forms a pipeline of formatters before actual log dispatching
    '''

    formatters = Attribute(
            '''List of formatters that compose pipeline.
            ''')
    writer = Attribute(
            '''The output sink in the pipeline that does the actual writing.
            '''
            )
    
    def execute( message, stream=streams.STDOUT, *pargs, **kwargs):
        '''Execute pipleline on message.

        @param message: message for outputting
        @type  message: string
        @param  stream: stream to output on
        @type   stream: integer       
        '''
        
    def __call__( message, stream, *pargs, **kwargs ):
        '''Calls execute with given arguments.
        '''
        

# IOutputPipeline

class OutputPipeline:

    implements(IOutputPipeline)

    def __init__(self, formatters=None, writer=None):
        self.formatters = (formatters,[])[formatters == None]
        self.writer     = (writer, DefaultWriter())[writer == None]

    def execute(self, msg, stream=streams.STDOUT, *pargs, **kwargs):
        for formatter in self.formatters:
            msg = formatter.format(msg, stream=stream, *pargs, **kwargs)
        self.writer.write(msg, stream=stream, *pargs, **kwargs)

    def __call__(self, msg, stream=streams.STDOUT, *pargs, **kwargs):
        self.execute(msg, stream=streams.STDOUT, *pargs, **kwargs)

# OutputPipeline 
     
###############################################################################
# Writers
#

class IWriter(Interface):
    
    '''The actual writer in the aspout pipeline.
    This encapsulates any device/network-bound output operation. 
    '''
    
    def write( message, stream=streams.STDOUT, *pargs, **kwargs ):
        '''Write message.

        @param message: message for outputting
        @type  message: string
        @param  stream: stream to output on
        @type   stream: integer       
        '''
        
    def __call__( message, stream, *pargs, **kwargs ):
        '''Calls write with given arguments
        '''
        
# IWriter

class CallableWriter:
    
    implements( IWriter )

    def write ( self, message, stream=streams.STDOUT, *pargs, **kwargs ):
        pass

    def __call__( self, message, *pargs, **kwargs ):
        self.write( self, message, *pargs, **kwargs )

# CallableWriter

class DefaultWriter( CallableWriter ):
    pass
# DefaultWriter

class ConsoleWriter ( CallableWriter ):
    
    def __init__(self):
        self.write_funcs = { 
            streams.STDOUT : sys.stdout.write,
            streams.STDERR : sys.stdout.write
        }
    def write(self, msg, stream=streams.STDOUT):
        if self.write_funcs.has_key(stream):
            self.write_funcs[stream]( '%s\n' % msg )
        else: self.write_funcs[streams.ERR]( '%s\n' % msg)
        
# ConsoleWriter singleton

###############################################################################
# Formatters
#

class IFormatter (Interface):

    '''I format a message.
    '''
    
    def format( message, stream=streams.STDOUT, *pargs, **kwargs):
        '''I return a formatted message to send down pipeline.
        
        @param message: message for outputting
        @type  message: string
        @param  stream: stream to output on
        @type   stream: integer       
        '''

# IFormatter
    
class CallingContextFormatter: # WARNING: kind of SLOW (but good for debugging)
                                 
    implements( IFormatter )
    
    def format(self, msg, stream=streams.STDOUT, *pargs, **kwargs):
        try:
            callers_frame = inspect.stack()[1][0]
            loop_counter = 0
            while callers_frame.f_globals['__name__'] in _io_internal_names:
                # need to go one more up in the stack
                del callers_frame
                callers_frame = inspect.stack()[2+loop_counter][0]
                loop_counter += 1
                if loop_counter == 64: break # this check need not be here! :-o !
            meta = '%s[%d]:'%(callers_frame.f_globals['__name__'], \
                    callers_frame.f_lineno)
        finally:
            del callers_frame
        return '%s %s'%(meta, msg)
# CallingContextFormatter

class TimeFormatter:
    implements( IFormatter )
    def format( self, msg, stream=streams.STDOUT, *pargs, **kwargs ):
        return '(%s) %s' % (asctime(), msg)
# TimeFormatter
        
###############################################################################
# singlentons
# writers        
default_writer = DefaultWriter()
console_writer = ConsoleWriter()
# pipelines
default_output_pipeline = OutputPipeline(writer=default_writer)
# formatters
calling_context_formatter = CallingContextFormatter()
time_formatter = TimeFormatter()

###############################################################################
# REGISTRY FOR ARBITERS
        
arbiters_registry = {}

def register_arbiters(name, arbiter_seq ):
    '''register arbiter sequence 

    @param arbiter_seq: an arbiter sequence that provides IWriterArbiterSequence interface
    @type  arbiter_seq: PyObject
    '''
    # Some basic Q.A. here:
    # Make sure all the components of the arbiter sequence provide
    # the necessary interfaces
    assert IWriterArbiterSequence.providedBy( arbiter_seq )
    for arbiter in arbiter_seq:
        assert IWriterAribiter.providedBy( arbiter )
        for pipeline in arbiter.pipelines:
            assert IOutputPipeline.providedBy( pipeline )
            for formatter in pipeline.formatters:
                assert IFormatter.providedBy( formatter )
            assert IWriter.providedBy( pipeline.writer )
    _acquire_lock()
    try:
        arbiters_registry[name] = arbiter_seq
    finally:
        _release_lock()
        

# The user need not care about essoteric things like Arbiters,
# hence 'getlogger' instead of 'getarbiter' etc.
def getlogger():
    '''
    Get configured logger instance for the calling module.

    @return logger instance
    @rtype IWriterArbiter
    @see xix._io
    '''
    callers_frame = None
    try:
        callers_frame = inspect.stack()[1][0]
        name = callers_frame.f_globals['__name__']
    finally:
        del callers_frame
    if name in arbiters_registry:
        # N.B. This will change! We need to return a WriterArbiter.
        return arbiters_registry[name]
    else:
        #default = StandardArbiter(writers=[default_writer,])
        default = WriterArbiterSequence([
                StandardArbiter(pipelines=[default_output_pipeline])
                ])
        register_arbiters(name, default)
        return default

# -=eof=
