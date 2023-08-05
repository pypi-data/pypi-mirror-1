import copy

from parley.proxy import ActorProxy, NoSuchActor
from parley.actor import AbstractActor

class AbstractController(object):
    '''
    To create a working actor controller, subclasses typically will
    have to, at a minimum, set ActorClass and implement
    _current_actor_id.
    '''
    # Subclasses must set this member variable
    ActorClass = AbstractActor
    
    def __init__(self):
        self.actors = {}
        self._next_id = 0
        # maps id -> actor proxy object
        self.proxies = {}
        # actors monitoring other actors: maps id -> set of ids
        self.links = {}
        # maps str -> actor proxy object
        self.registered_names = {}
        
        self.trace = None

    def _spawn(self, target, args, kwargs, link=False):
        # Prevent accidental sharing of data via arguments
        args = copy.deepcopy(args)
        kwargs = copy.deepcopy(kwargs)
        
        _id = self._next_id
        self._next_id += 1
        self.actors[_id] = actor = self.ActorClass(self, _id,
                                                   target, args, kwargs)
        self.proxies[_id] = proxy = ActorProxy(self, _id)
        self.links[_id] = set()
        if link:
            self.link(proxy)
        actor.go()
        return proxy
    def spawn_link(self, target, *args, **kwargs):
        return self._spawn(target, args, kwargs, link=True)
    def spawn(self, target, *args, **kwargs):
        return self._spawn(target, args, kwargs)

##     # This is currently a bad idea, since the main thread cannot fully
##     # participate in the actor model. In particular, there is no way
##     # to notify linked actors if the main thread has quit or aborted.
##     def spawn_main(self):
##         '''Like spawn, but sets up the new actor in the current
##         execution context instead of creating a new one.
##         '''
##         _id = self._next_id
##         self._next_id += 1
##         self.actors[_id] = actor = self.ActorClass(self, _id, None, None, None)
##         # Do this in the current execution context (rather than spawning)
##         actor.register_id()
##         self.proxies[_id] = proxy = ActorProxy(self, _id)
##         self.links[_id] = set()

    def send(self, target_id, msg):
        # Prevent actors from accidentally sharing references to objects
        # contained in messages
        msg = copy.deepcopy(msg)
        # TODO: check to see if target_id is local
        try:
            dest = self.actors[target_id]
        except KeyError:
            raise NoSuchActor
        if self.trace:
            self.trace.write('%s < %s\n' % (dest, msg))
        self.actors[target_id].put_msg(msg)

    def send_signal(self, target_id, msg):
        try:
            dest = self.actors[target_id]
        except KeyError:
            raise NoSuchActor
        if self.trace:
            self.trace.write('%s ! %s\n' % (dest, msg))
        dest.put_signal(msg)

    def _create_link(self, a, b):
        self.links[a].add(b)
    def _remove_link(self, a, b):
        self.links[a].discard(b)
        
    def link(self, target):
        origin_id = self._current_actor_id()
        try:
            self._create_link(origin_id, target.id)
            self._create_link(target.id, origin_id)
        except KeyError:
            raise NoSuchActor(target)
        
    def unlink(self, target):
        origin_id = self._current_actor_id()
        try:
            self._remove_link(origin_id, target.id)
            self._remove_link(target.id, origin_id)
        except KeyError:
            raise NoSuchActor(target)

    def _quit(self, actor_id):
        # This is O(# of current running actors). An alternative
        # is to never remove dead actors from self.links, which has
        # different performance implications.
        for link_set in self.links.values():
            link_set.discard(actor_id)
        del self.actors[actor_id]
        del self.proxies[actor_id]
        del self.links[actor_id]

    def alert_exception(self, origin_id, e):
        origin = self.proxies[origin_id]
        # copy the set in case it changes as a result of the messages we send
        for listener_id in self.links[origin_id].copy():
            try:
                self.proxies[listener_id]._send_signal(e, origin)
            except (KeyError, NoSuchActor):
                # the actor deleted itself in the middle of this function
                continue
        self._quit(origin_id)

    def alert_quit(self, origin_id):
        origin = self.proxies[origin_id]
        # Do we want to actually send a quit message here?
        # Recipients may not be expecting it.
        for listener_id in self.links[origin_id].copy():
            try:
                self.proxies[listener_id].send('quit', origin)
            except (KeyError, NoSuchActor):
                continue
        self._quit(origin_id)

    def _current_actor_id(self):
        '''Return the current actor ID.

        Subclasses can implement this function by, for example,
        storing the current actor ID in threadlocal storage.
        '''
        raise NotImplementedError
    def _current_actor(self):
        return self.actors[self._current_actor_id()]
    def _current_actor_proxy(self):
        return self.proxies[self._current_actor_id()]

    def schedule(self):
        '''Yield control of execution.

        Cooperatively scheduled execution models
        will have to override this function.
        '''
        pass

    def shutdown(self):
        '''Send quit signals to every actor and attempt to shut down
        the node.

        This function is called when any actor raises SystemExit. It
        does not attempt to force actors to shut down: if an actor
        does not call recv(), or if it is trapping signals and not
        handling them properly, it will not shut down.'''
        origin = self._current_actor()
        if self.trace:
            self.trace.write('Shutdown requested by %s\n' % origin)
        for a in self.proxies.values():
            if a.id == origin.id:
                continue
            try:
                a._send_signal(SystemExit, origin.id)
            except (KeyError, NoSuchActor):
                # the actor deleted itself in the middle of this function
                continue

    def register(self, actor_proxy, name):
        self.registered_names[name] = actor_proxy

    def unregister(self, name):
        try:
            del self.registered_names[name]
        except KeyError:
            pass

    def lookup(self, name):
        try:
            return self.registered_names[name]
        except KeyError:
            raise NoSuchActor(name)

##     def _synchronized(fn, self):
##         def wrap(*args, **kwargs):
##             self._acquire_lock()
##             try:
##                 fn(*args, **kwargs)
##             finally:
##                 self._release_lock()
##         return wrap
        
##     def _acquire_lock(self):
##         raise Exception
##     def _release_lock(self):
##         raise Exception
    

