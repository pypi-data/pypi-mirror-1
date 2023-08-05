'''
lockserver.py - demonstrates a server actor that allows one client
at a time to access a dictionary.

This example is loosely based on an example from the Erlang book.
(Concurrent Programming in Erlang, Armstrong et al, 1993, p. 135)
'''

from parley.helpers import StateMachine, StopActor, \
     forward_exceptions, DoNotReply
from parley import *

import time

class LockServer(StateMachine):
    class DictionaryLocked(Exception):
        pass
    
    def __init__(self):
        self.state = 'unlocked'
        self.dict = {}
        self.owner = None
        set_name('LockServer')
        StateMachine.__init__(self)

    def locked_filter(self, (msg, sender, args, kwargs)):
        return sender == self.owner
    def unlocked_filter(self, (msg, sender, args, kwargs)):
        # TODO: it would be nice if StateMachine did this test for us
        return msg in ['acquire','quit']
        
    def unlocked_acquire(self, sender):
        self.state = 'locked'
        self.owner = sender
        link(sender)

    def unlocked_quit(self, sender):
        # The main actor is linked to us: when it quits, so should we
        raise StopActor

    @forward_exceptions([KeyError])
    def locked_read(self, sender, key):
        return self.dict[key]

    def locked_write(self, sender, key, value):
        self.dict[key] = value
    
    @forward_exceptions([KeyError])
    def locked_delete(self, sender, key):
        del self.dict[key]
    
    def locked_release(self, sender):
        self.state = 'unlocked'
        self.owner = None
        unlink(sender)

    def locked_quit(self, sender):
        self.state = 'unlocked'
        self.owner = None
        raise DoNotReply

def client():
    set_name('client')
    import random

    d = lookup('LockServer')
    d.acquire()
    print me(), 'got lock'
    d.write(me().id, True)
    # time.sleep blocks, so this will not work with tasklets
    time.sleep(random.random()*2)
    print 'State of dictionary:'
    for i in range(num_clients):
        try:
            print '%d: %s' % (i, d.read(i))
        except RPCException:
            pass
    d.release()
    print me(), 'released lock'

num_clients = 10

def main():
    trace_on()
    set_name('main')
    d = spawn_link(LockServer)
    register(d, 'LockServer')
    for i in range(num_clients):
        spawn_link(client)
    for i in range(num_clients): # wait for quit messages from clients
        #print 'main waiting for message', i
        print recv()

if __name__=='__main__':
    start_tasklet_controller(main)
