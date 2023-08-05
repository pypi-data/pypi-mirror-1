from parley import StopActor

class AbnormalExit(Exception):
    '''An actor will raise this exception if it terminated by
    means of an uncaught exception.'''
    def __init__(self, e=''):
        self.inner_exception = e
    def __str__(self):
        if self.inner_exception is Exception:
            return '%s: %s' % (self.inner_exception.__class__,
                               self.inner_exception)
        else:
            return str(self.inner_exception)

class AbstractQueue:
    '''Controllers should define a queue implementation
    having this interface.'''
    def get(self):
        raise NotImplementedError
    def put(self, o):
        raise NotImplementedError
    def get_nowait(self):
        raise NotImplementedError

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
            self.target(*self.args, **self.kwargs)
        except StopActor:
            # Actor wants to safely exit
            self.controller.alert_quit(self.id)
        except Exception, e:
            #print self, 'propagating exception', e.__class__, e
            self.controller.alert_exception(self.id, AbnormalExit(e))
            # Doesn't really matter, since the thread is about to
            # expire anyway, but it's nice to get the traceback
            # on the console
            #print self, 'raising exception'
            raise
        else:
            self.controller.alert_quit(self.id)
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

    def _handle_signal(self, signal):
        '''If this function is called, we know that a signal is waiting.
        Depending on the value of self.trap_exceptions, we either
        raise the signal as an exception or return it as a message.'''
        exception, origin = signal
        if self.trap_exceptions:
            # convert the signal to an ordinary message and return it
            return ('abort', origin, (exception,), {})
        else:
            # wrap the signal and propagate it
            raise AbnormalExit(exception)
    
    def recv(self, msg_filter=None, wait=True):
        if msg_filter is None:
            msg_filter = lambda *args: True
        signal = self.signal_queue.get_nowait()
        if signal:
            msg = self._handle_signal(signal)
            self.msg_queue.put(msg)
        return self._next_message(msg_filter, wait)

    def _next_message(self, msg_filter, wait):
        # Return the first waiting message that passes the filter,
        # placing skipped messages in an overflow list.
        for i, msg in enumerate(self._overflow):
            if msg_filter(msg):
                return self._overflow.pop(i)
        while True:
            #print self.name, 'waiting for msg'
            if wait:
                msg = self.msg_queue.get()
            else:
                msg = self.msg_queue.get_nowait()
            #print self.name, 'received', msg
            if msg == 'SIGNAL':
                # This could happen in two ways:
                # 1. a signal has arrived while we were blocking
                # 2. a signal arrived earlier and this message is stale
                signal = self.signal_queue.get_nowait()
                if signal:
                    # this will either return the signal as a message
                    # or raise an exception
                    msg = self._handle_signal(signal)
            if not wait and msg == None:
                return msg
            else:
                if msg_filter(msg):
                    return msg
                else:
                    self._overflow.append(msg)
