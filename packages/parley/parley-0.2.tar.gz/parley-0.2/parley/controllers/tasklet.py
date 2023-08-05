import stackless
import sys
import traceback

from parley.actor import AbstractActor
from parley.controller import AbstractController

def _copy(l, r):
    while True:
        msg = r.receive()
        l.send(msg)

# This is like ChannelWrapper, but it uses two channels and spawns
# a tasklet to copy messages from one to the other.
# For some reason, this makes it harder for stackless to detect deadlocks
# (which is a good thing for us, since we are trying to match the behavior
# of the threaded execution model, which does not provide deadlock detection).
class WackyChannelWrapper:
    '''Wraps stackless channels to give them a queue-like interface.'''
    def __init__(self):
        self._r_channel = stackless.channel()
        self._s_channel = stackless.channel()
        self._copier = stackless.tasklet(_copy)
        self._copier(self._r_channel, self._s_channel)

    def get(self):
        return self._r_channel.receive()

    def put(self, data):
        return self._s_channel.send(data)

    def get_nowait(self):
        # This only works if we are using stackless' non-preemptive execution
        # model
        if self._r_channel.balance > 0:
            return self._r_channel.receive()
        else:
            return None

class ChannelWrapper:
    '''Wraps stackless channels to give them a queue-like interface.'''
    def __init__(self):
        self._channel = stackless.channel()

    def get(self):
        return self._channel.receive()

    def put(self, data):
        return self._channel.send(data)

    def get_nowait(self):
        # This only works if we are using stackless' non-preemptive execution
        # model
        if self._channel.balance > 0:
            return self._channel.receive()
        else:
            return None

class TaskletActor(AbstractActor):
    QueueClass = WackyChannelWrapper

    def register_id(self):
        self.controller.tasklets[id(stackless.getcurrent())] = self.id
        
    def run(self):
        try:
            AbstractActor.run(self)
        except:
            # Swallow the exception: stackless python normally terminates
            # the whole program if any tasklet raises an exception
            #print self, 'printing exception and stopping'
            traceback.print_tb(sys.exc_info()[2])
    def go(self):
        self.tasklet = stackless.tasklet(self.run)
        self.tasklet()
    
class TaskletController(AbstractController):
    ActorClass = TaskletActor

    def __init__(self, *args, **kwargs):
        # Maps tasklet ID to actor ID
        self.tasklets = {}
        
        super(TaskletController, self).__init__(*args, **kwargs)

    def alert_exception(self, origin_id, e):
        traceback.print_exc()
        return AbstractController.alert_exception(self, origin_id, e)
        
    def _current_actor_id(self):
        return self.tasklets[id(stackless.getcurrent())]

