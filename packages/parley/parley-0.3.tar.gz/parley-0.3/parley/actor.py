from parley import StopActor

class AbnormalExit(Exception):
    '''An actor will raise this exception if it terminated by
    means of an uncaught exception.'''
    def __init__(self, e=''):
        self.inner_exception = e
    def __str__(self):
        if isinstance(self.inner_exception, Exception):
            return '%s: %s' % (self.inner_exception.__class__.__name__,
                               self.inner_exception)
        else:
            return str(self.inner_exception)

class Become(Exception):
    '''
    This exception is thrown by the become() function to transfer control
    to the new target.
    '''
    def __init__(self, target, args, kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs

# Disabled - we in fact want to send messages to linked actors in every case.
# (these might be remote actors, who deserve to receive the message
# about our shutdown.)
## class TerminateActor(Exception):
##     '''
##     This exception is thrown in response to a shutdown signal. It
##     causes the actor to quit without sending notice to its linked actors.
##     '''
##     pass

class AbstractQueue:
    '''Controllers should define a queue implementation
    having this interface.'''
    def get(self):
        raise NotImplementedError
    def put(self, o):
        raise NotImplementedError
    def get_nowait(self):
        raise NotImplementedError

class SimpleQueue(AbstractQueue):
    '''A wrapper around a list objects to implement the AbstractQueue
    interface.'''
    def __init__(self):
        self._q = []
    def put(self, o):
        self._q.append(o)
    def get(self):
        return self._q.pop(0)
    def get_nowait(self):
        # This will not work correctly in a preemptive execution model
        if self._q:
            return self._q.pop(0)
        else:
            return None

class AbstractActor(object):
    # Subclasses must specify a QueueClass having get and put methods.
    QueueClass = AbstractQueue
    
    def __init__(self, controller, _id, target, args, kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs
        
        self.msg_queue = self.QueueClass()
        self.signal_queue = self.QueueClass()
        self.id = _id
        self.controller = controller
        self.trap_exceptions = False
        self._overflow = []
        self.name = 'actor'

    def __str__(self):
        return '%s(id=%d)' % (self.name, self.id)
    
    # This function should be spawned in a new thread of execution
    def run(self):
        '''Hand off control to self.target.

        This function will be spawned in a new frame of execution.'''

        self.register_id()
        try:
            while True:
                try:
                    self.target(*self.args, **self.kwargs)
                except Become, e:
                    self.target = e.target
                    self.args = e.args
                    self.kwargs = e.kwargs
                else:
                    break
        except StopActor: # Actor wants to safely exit
            pass
        except SystemExit:
            self.controller.shutdown()
        except Exception, e:
            #print self, 'propagating exception', e.__class__, e
            self.controller.alert_exception(self.id, AbnormalExit(e))
            raise
        self.controller.alert_quit(self.id)
        #print 'done'
        # TODO: check for any missed signals

    # This function should be overridden to call self.run in a new thread
    # of execution, typically after setting some threadlocals.
    def go(self):
        '''Spawn self.run in a new frame of execution.

        This function is called by the controller when the created
        actor is to be spawned.
        '''
        raise NotImplementedError

    def register_id(self):
        '''Register self.id such that it can be retrieved
        by controller._get_current_actor_id()
        (e.g. by storing it in threadlocals).'''
        raise NotImplementedError

    #
    # Get and put functions. These should only be invoked
    # by the controller responsible for this actor.
    #
    def put_msg(self, msg):
        '''Deliver the given message to this actor.'''
        self.msg_queue.put(msg)
    def put_signal(self, msg):
        self.signal_queue.put(msg)
        # Wake us up in case we are blocked on a recv()
        self.msg_queue.put('SIGNAL')
    def get_msg(self):
        '''Remove one message from the queue,
        blocking if none are available.'''
        return self.msg_queue.get()
    def get_msg_nowait(self):
        '''Remove one message from the queue if one exists,
        otherwise return None.'''
        return self.msg_queue.get_nowait()
    
    def _handle_signal(self, signal):
        '''
        Handle a received signal.
        
        Depending on the value of self.trap_exceptions, we either
        raise the signal as an exception or place it in the message queue.
        '''
        exception, origin = signal
        if self.trap_exceptions:
            self.msg_queue.put(('abort', origin, (exception,), {}))
        else:
            if exception is SystemExit or isinstance(exception, SystemExit):
                # This was a requested exception, so exit quietly
                raise StopActor
            else:
                # wrap the signal and propagate it
                raise AbnormalExit(exception)

    def _check_for_signals(self):
        '''Check if any signals are waiting in the signal queue.'''
        signal = self.signal_queue.get_nowait()
        if signal:
            self._handle_signal(signal)
        
    def recv(self, msg_filter=None, wait=True):
        if msg_filter is None:
            msg_filter = lambda *args: True
        self._check_for_signals()
        return self._next_message(msg_filter, wait)

    def schedule(self):
        '''Check for signals and ask the controller
        to yield control of execution.'''
        self._check_for_signals()
        self.controller.schedule()

    def _next_message(self, msg_filter, wait):
        # Return the first waiting message that passes the filter,
        # placing skipped messages in an overflow list.
        for i, msg in enumerate(self._overflow):
            if msg_filter(msg):
                return self._overflow.pop(i)
        while True:
            #print self.name, 'waiting for msg'
            if wait:
                msg = self.get_msg()
            else:
                msg = self.msg_queue.get_nowait()
                if msg is None:
                    return
            #print self.name, 'received', msg
            if msg == 'SIGNAL':
                self._check_for_signals()
                # If we reach this point, either we are trapping exceptions
                # or the 'SIGNAL' message was stale.
                continue
            
            if msg_filter(msg):
                return msg
            else:
                self._overflow.append(msg)
