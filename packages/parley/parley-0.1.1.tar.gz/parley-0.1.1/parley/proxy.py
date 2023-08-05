from parley import RPCException

class NoSuchActor(RPCException):
    '''This exception is raised upon sending a message to an actor that
    does not exist.'''
    pass

class RPCReplyException(RPCException):
    '''This exception is raised by the .call() method of ActorProxy
    objects if the target actor responds with a message that is not
    parseable as an RPC reply.'''
    pass

class ActorProxy(object):
    def __init__(self, controller, actor_id):
        self.controller = controller
        self.id = actor_id

    def __repr__(self):
        return '<ActorProxy(id=%d)>' % (self.id)

    def __cmp__(self, other):
        # TODO: make sure both are on same controller
        return cmp(self.id, other.id)

    def __hash__(self):
        # should this be implemented ???
        # should we index controller dictionaries with the proxy objects?
        return self.id
    
    def send(self, msg_name, sender, *args, **kwargs):
        '''
        Sends the message (msg_name, sender, args, kwargs) to this actor.
        '''
        #if 'reply_to' not in kwargs:
        #    kwargs['reply_to'] = self.controller._current_actor_proxy()
        self.controller.send(self.id, (msg_name, sender, args, kwargs))

    def send_raw(self, msg):
        '''Send this actor an arbitrary object as a message.

        Use this function to send messages that are not 4-tuples.
        '''
        self.controller.send(self.id, msg)

    def _send_signal(self, value, sender):
        self.controller.send_signal(self.id, (value, sender))

    def _with_link(self, sender, action):
        '''Make a link to the given actor that exists for the duration
        of the call to action()'''
        self.controller._create_link(self.id, sender.id)
        #try:
        ret = action()
        #finally:
        try:
            self.controller._remove_link(self.id, sender.id)
        except KeyError:
            # this occurs if we have just quit
            pass
        return ret
        
    def call(self, msg_name, sender, *args, **kwargs):
        '''
        Sends the message (msg_name, sender, args, kwargs) to this actor,
        then hooks into the recv() function of the calling actor to block
        for an RPC response from this actor.
        '''
        
        def _is_rpc_reply(msg):
            return msg[0] in ('reply', 'exception', 'quit') and msg[1] == self
        
        #This method pokes around a LOT in the calling actor.
        # (i.e. controller._current_actor())
        #Properly, it should be expressed as:
        #  src.call(dest, ...)
        #but we allow this ugly implementation so we can
        # present the nice interface dest.call(...)
        def send_and_recv():
            self.send(msg_name, sender, *args, **kwargs)
            return self.controller._current_actor().recv(_is_rpc_reply)
        try:
            has_link = (sender.id in self.controller.links[self.id])
        except KeyError: # we apparently no longer exist
            raise NoSuchActor(self)
        if has_link:
            msg = send_and_recv()
        else:
            msg = self._with_link(sender, send_and_recv)

        try:
            method, sender, args, kwargs = msg
        except ValueError:
            raise RPCReplyException(
                'Invalid RPC reply: expected 4-tuple, got ' + str(msg))
        if len(args) == 0:
            # This corresponds with the semantics of return statements
            ret = None
        elif len(args) == 1:
            ret = args[0]
        else:
            raise RPCReplyException(
                'Invalid RPC reply: '
                'expected singleton tuple as third item, got ' + str(args))
        
        if method == 'reply':
            return ret
        elif method == 'exception':
            if ret is None:
                raise RPCReplyException(
                    'Invalid RPC reply: attempted to raise None as exception')
            else:
                raise ret
        elif method == 'quit':
            # TODO: should we raise an exception indicating that we
            # quit in response to this call? The client may or may not
            # have been expecting us to have done so.
            return None
        else:
            raise RPCReplyException(
                'Invalid RPC reply (unknown message name %s)' % method)

    def __getattr__(self, msg_name):
        def msg_sender(*args, **kwargs):
            '''Wrapper to send a message with a msg_name equal to the name
            by which this function is accessed and with a sender equal to the
            current actor.

            Accepts an extra keyword argument "async" that determines
            whether to use send() or call() to send the message. This argument
            is not forwarded to the destination actor.
            '''
            if 'async' in kwargs and kwargs.pop('async'):
                fn = self.send
            else:
                fn = self.call
            sender = self.controller._current_actor_proxy()
            return fn(msg_name, sender, *args, **kwargs)
        return msg_sender

