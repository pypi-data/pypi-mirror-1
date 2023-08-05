from parley.proxy import ActorProxy, NoSuchActor

class AbstractController(object):
    # Subclasses must set this member variable
    ActorClass = None
    
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

    def _synchronized(fn, self):
        def wrap(*args, **kwargs):
            self._acquire_lock()
            try:
                fn(*args, **kwargs)
            finally:
                self._release_lock()
        return wrap
        
    def _spawn(self, target, args, kwargs, link=False):
        id = self._next_id
        self._next_id += 1
        self.actors[id] = actor = self.ActorClass(self, id)
        self.proxies[id] = proxy = ActorProxy(self, id)
        self.links[id] = set()
        if link:
            self.link(proxy)
        actor.go(target, *args, **kwargs)
        return proxy
    def spawn_link(self, target, *args, **kwargs):
        return self._spawn(target, args, kwargs, link=True)
    def spawn(self, target, *args, **kwargs):
        return self._spawn(target, args, kwargs)

    def send(self, target_id, msg):
        # TODO: check to see if target_id is local
        try:
            dest = self.actors[target_id]
        except KeyError:
            raise NoSuchActor
        if self.trace:
            self.trace.write('%s < %s\n' % (dest, msg))
        self.actors[target_id].msg_queue.put(msg)

    def send_signal(self, target_id, msg):
        try:
            dest = self.actors[target_id]
        except KeyError:
            raise NoSuchActor
        if self.trace:
            self.trace.write('%s ! %s\n' % (dest, msg))
        # TODO: is this sequence of commands causing the tasklet controller
        # to deadlock???
        dest.signal_queue.put(msg)
        # If the actor is blocked on a recv, wake it up
        dest.msg_queue.put('SIGNAL')

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
                pass
        self._quit(origin_id)

    def alert_quit(self, origin_id):
        origin = self.proxies[origin_id]
        # Do we want to actually send a quit message here?
        # Recipients may not be expecting it.
        for listener_id in self.links[origin_id].copy():
            try:
                self.proxies[listener_id].send('quit', origin)
            except (KeyError, NoSuchActor):
                pass
        self._quit(origin_id)

    def _current_actor_id(self):
        '''Subclasses should override this function to return the
        current actor ID -- for example, by looking it up in threadlocal
        storage.'''
        raise Exception
    def _current_actor(self):
        return self.actors[self._current_actor_id()]
    def _current_actor_proxy(self):
        return self.proxies[self._current_actor_id()]

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

##     def _acquire_lock(self):
##         raise Exception
##     def _release_lock(self):
##         raise Exception
    

