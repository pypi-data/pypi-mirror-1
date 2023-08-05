import sys

class StopActor(Exception):
    '''
    Raise this exception to cause an actor to terminate normally.
    RPC servers should catch this exception to send a blank reply
    before quitting.
    '''
    pass

class RPCException(Exception):
    '''Indicates a generic failure during an RPC call.'''
    pass

class RemoteException(RPCException):
    '''This exception indicates that the remote actor responded to a
    message by sending an exception.
    '''
    def __init__(self, e=''):
        self.remote_exception = e
        RPCException.__init__(self)
    def __str__(self):
        if self.remote_exception is Exception:
            return '%s: %s' % (self.remote_exception.__class__,
                               self.remote_exception)
        else:
            return str(self.remote_exception)

# TODO: replace None with dummy object that raises a more helpful exception
_controller = None

def start_thread_controller():
    '''Cause actors to be executed using traditional kernel threads.'''
    global _controller
    import parley.controllers.thread as model

    # I'm not sure what havoc would result if another controller
    # is already running.
    assert _controller is None
    _controller = model.ThreadController()

def start_tasklet_controller():
    '''Cause actors to be executed using stackless tasklets.'''
    global _controller
    import parley.controllers.tasklet as model
    #import stackless

    assert _controller is None
    _controller = model.TaskletController()
    #stackless.run()

def trace_on(out_file=sys.stdout):
    '''Cause messages to be printed to the specified file (by default stdout)'''
    _controller.trace = out_file
def trace_off():
    '''Stop the tracing of sent messages'''
    _controller.trace = None

def recv(msg_filter=None):
    '''
    Return a waiting message from the current actor, or block
    (allowing other threads to continue) until a message is available.

    The optional msg_filter argument should accept a message as
    an argument and return True or False to determine whether to
    return the message or leave it for later.
    '''
    return _controller._current_actor().recv(msg_filter)

def me():
    '''
    Return a proxy object for the currently running actor.
    '''
    return _controller._current_actor_proxy()

# All of these have an extra layer of indirection
# because our controller object does not exist when this module
# is imported.
def spawn(actor, *args, **kwargs):
    '''Spawn a new actor in a new thread of execution.

    As with the built-in "apply" function,
    the first argument can be any callable object, and remaining
    arguments are forwarded to that function.
    '''
    return _controller.spawn(actor, *args, **kwargs)
def spawn_link(actor, *args, **kwargs):
    '''Spawn a new actor and link the current actor to it.

    Equivalent to:
      a=spawn(...)
      link(a)
    but executed atomically: i.e., the spawned actor will not be started
    until it has been linked to the calling actor.
    '''
    return _controller.spawn_link(actor, *args, **kwargs)
def link(target):
    '''Create a bidirectional link to the target actor.

    If one linked actor terminates abnormally, the other will
    raise an AbnormalExit exception upon its next call to recv().
    Similarly, if one actor terminates normally, a quit message
    will be sent to the other.
    '''
    return _controller.link(target)
def unlink(target):
    '''Cancel the bidirectional link to the target actor.'''
    return _controller.unlink(target)

def set_name(name):
    '''Set the internal name of the current actor. This is not any sort
    of globally reachable ID; this name is just to identify the actor
    for debugging purposes (e.g. if trace_on() has been called).'''
    _controller._current_actor().name = name
    
def register(target, name):
    '''Register the target actor proxy as being
    available under the given name.'''
    return _controller.register(target, name)
def unregister(name):
    '''Unregister the actor proxy associated with the given name.'''
    return _controller.unregister(name)
def lookup(name):
    '''Return the actor proxy associated with the given name.

    Raises NoSuchActor if the name has not been registered.'''
    return _controller.lookup(name)
