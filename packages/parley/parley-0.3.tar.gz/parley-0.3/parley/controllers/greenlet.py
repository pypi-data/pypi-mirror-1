import traceback

from py.magic import greenlet

from parley.actor import AbstractActor, SimpleQueue
from parley.controller import AbstractController

class ListNode:
    def __init__(self, data):
        self.data = data
        self.next = None

class GreenletActor(AbstractActor):
    QueueClass = SimpleQueue

    def __init__(self, *args, **kwargs):
        self.runnable = True
        super(GreenletActor, self).__init__(*args, **kwargs)
    
    def register_id(self):
        self.controller.greenlets[id(greenlet.getcurrent())] = self.id

    def put_msg(self, msg):
        self.runnable = True
        super(GreenletActor, self).put_msg(msg)
        self.controller.schedule()

    def put_signal(self, msg):
        self.runnable = True
        super(GreenletActor, self).put_signal(msg)
        self.controller.schedule()

    def get_msg(self):
        while True:
            try:
                return self.msg_queue.get()
            except IndexError: # pop from empty list
                self.runnable = False
                self.controller.schedule()

    def get_msg_nowait(self):
        msg = self.msg_queue.get_nowait()
        if msg is None:
            self.controller.schedule()
        return msg
        
    def go(self):
        self.greenlet = greenlet(run=self.run)
        self.greenlet.parent = self.controller.main_greenlet
        self.greenlet.switch()

class GreenletController(AbstractController):
    ActorClass = GreenletActor

    def __init__(self, *args, **kwargs):
        self.main_greenlet = greenlet.getcurrent()
        self._current = None
        self.greenlets = {} # Maps greenlet ID to actor ID
        
        super(GreenletController, self).__init__(*args, **kwargs)
        

    def _current_actor_id(self):
        return self.greenlets[id(greenlet.getcurrent())]

    def _spawn(self, target, args, kwargs, link=False):
        # TODO: test if this is an external actor
        #if self._current_actor_id()
        proxy = super(GreenletController, self)._spawn(
            target, args, kwargs, link)
        self._insert_actor(proxy.id)
        return proxy
    
    def _insert_actor(self, actor_id):
        to_insert = ListNode(actor_id)
        if self._current == None:
            self._current = to_insert
            self._current.next = self._current
        else:
            temp = self._current.next
            self._current.next = to_insert
            to_insert.next = temp
    def _next_actor(self):
        # advance through list, checking actor.runnable
        start = prev = self._current
        while True:
            self._current = self._current.next
            try:
                actor = self.actors[self._current.data]
            except KeyError:
                #print 'removing', self._current.data
                if self._current == start:
                    return None
                prev.next = self._current.next
                continue
            if actor.runnable: # messages are waiting
                return actor
            if self._current == start:
                return None
            prev = self._current

    def schedule(self):
        greenlet.getcurrent().parent.switch()

    def run_forever(self):
        #print 'main greenlet is', greenlet.getcurrent()
        while True:
            next = self._next_actor()
            if next is None:
                if self.actors:
                    # Actors exist, but none are runnable - deadlock!
                    # TODO - do something else here.
                    #time.sleep(.1)
                    continue
                else:
                    # All actors have exited
                    return
            
            # TODO: swallow the exception in the child instead?
            try:
                #print 'switching to', next
                next.greenlet.switch()
            except KeyboardInterrupt:
                # Don't swallow this exception: we want the whole scheduler
                # to shut down.
                raise
            except:
                print 'Exception in', next
                traceback.print_exc()
