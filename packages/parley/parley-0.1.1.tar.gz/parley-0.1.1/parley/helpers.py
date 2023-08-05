'''
parley/helpers.py - various helper classes and functions for constructing actors
'''

from parley import *

class DoNotReply(Exception):
    '''Actors incorporating the parley.helpers classes can
    raise this exception to indicate that no response to the
    calling actor should be sent.'''
    pass

def forward_exceptions(lst):
    '''Wraps a function to translate certain exceptions into
    RemoteExceptions (which will typically be sent as messages
    to an RPC client).
    If the list of exceptions is not specified,
    all exceptions except StopActor are caught in this manner.

    Usage:
    @forward_exceptions([KeyError, ValueError])
    def foo(): ...
    '''
    def outer_wrap(fn):
        def wrap(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except StopActor:
                raise
            except Exception, e:
                if lst is None or e.__class__ in lst:
                    raise RemoteException(e)
                else:
                    raise
        return wrap
    return outer_wrap

def _send_rpc_reply(reply_to, action):
    try:
        ret = action()
    except StopActor:
        # Send a blank reply to complete the RPC
        # TODO: maybe rely on the framework to send a quit message?
        #reply_to.send('reply', me(), None)
        raise
    except DoNotReply:
        return
    except RemoteException, e:
        reply_to.send('exception', me(), e)
    else:
        reply_to.send('reply', me(), ret)

def function_actor(fn, loop=True):
    '''Wraps a function to act as an RPC server.

    The resulting actor will respond to the "quit" message by exiting
    and to any other message by calling the function and returning its
    return value as an RPC reply.
    
    If the parameter loop is False, the actor accepts one message
    and then exits; otherwise, the actor serves forever.'''
    def wrap(fn):
        msg, reply_to, args, kwargs = recv()
        if msg == 'quit':
            # Do not reply here: the fact that we received a quit message
            # indicates that the reply_to actor has terminated.
            #reply_to.send('reply', me())
            raise StopActor
        _send_rpc_reply(reply_to, lambda: fn(*args, **kwargs))
    
    def run_loop():
        while True:
            wrap(fn)
    def run_once():
        wrap(fn)
    
    if loop:
        return run_loop
    else:
        return run_once

class Dispatcher:
    '''
    Inherit from this class to create an actor that behaves as an RPC server:
    messages received get translated into function calls,
    and function return values (as well as exceptions) are translated
    into reply messages.

    If you override the __init__ function, call the parent __init__
    last to start the actor.
    '''
    def __init__(self):
        self._loop()

    def _loop(self):
        while True:
            msg, sender, args, kwargs = recv(self.filter)
            if (msg[0] == '_'
                or not self._pre_dispatch(msg, sender, args, kwargs)):
                continue
            _send_rpc_reply(sender, lambda: self._dispatch(
                msg, sender, args, kwargs))
            self._post_dispatch(self, msg, sender, args, kwargs)

    def _pre_dispatch(self, msg, sender, args, kwargs):
        return True
    def _dispatch(self, msg, sender, args, kwargs):
        try:
            fn = getattr(self, msg)
        except AttributeError:
            return self._default(msg, sender, args, kwargs)
        else:
            return fn(sender, *args, **kwargs)
    def _post_dispatch(self, msg, sender, args, kwargs):
        pass

    def _default(self, msg, sender, args, kwargs):
        pass
    
class StateMachine:
    '''Behaves like Dispatcher, but self.state (along with an underscore)
    is prepended to message names before they are looked up.'''
    def __init__(self):
        self._loop()

    def _loop(self):
        while True:
            pre_dispatch = self._state_getattr(
                '_pre_dispatch', lambda *args: True)
            post_dispatch = self._state_getattr(
                '_post_dispatch', lambda *args: None)
            msg_filter = self._state_getattr('filter')

            msg, sender, args, kwargs = recv(msg_filter)
            #print 'dispatching', (msg, sender, args, kwargs)
            _send_rpc_reply(sender, lambda: self._dispatch(
                msg, sender, args, kwargs))
            post_dispatch(self, msg, sender, args, kwargs)
        
    def _state_getattr(self, name, default=None):
        return getattr(self, '_'.join((self.state, name)), default)
    
    def _dispatch(self, msg, sender, args, kwargs):
        fn = self._state_getattr(msg)
        if fn is None:
            default = self._state_getattr('_default', self._default)
            return default(msg, sender, args, kwargs)
        else:
            return fn(sender, *args, **kwargs)

    def _default(self, msg, sender, args, kwargs):
        '''Default handler, called if (state)__default does not exist'''
        pass
    
