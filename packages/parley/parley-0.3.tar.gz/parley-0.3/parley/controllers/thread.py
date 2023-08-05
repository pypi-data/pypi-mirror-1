import threading
import Queue

from parley.actor import AbstractActor
from parley.controller import AbstractController

class ThreadQueue(Queue.Queue):
    def get_nowait(self):
        try:
            return self.get(timeout=0)
        except Queue.Empty:
            return None

class ThreadActor(AbstractActor):
    QueueClass = ThreadQueue

    def register_id(self):
        self.controller.threadlocals.id = self.id
        
    def go(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    # To make tracebacks nicer, have self.name also set the thread name
    def _set_name(self, name):
        self._name = name
        if hasattr(self, 'thread') and self.thread:
            self.thread.setName('%s(id=%d)' % (self._name, self.id))
    def _get_name(self):
        return self._name
    name = property(_get_name, _set_name)

class ThreadController(AbstractController):
    ActorClass = ThreadActor
    
    def __init__(self, *args, **kwargs):
        self.threadlocals = threading.local()
        #self.lock = threading.Lock()
        super(ThreadController, self).__init__(*args, **kwargs)

    def _current_actor_id(self):
        return self.threadlocals.id

##     def _acquire_lock(self):
##         self.lock.acquire()
##     def _release_lock(self):
##         self.lock.release()

