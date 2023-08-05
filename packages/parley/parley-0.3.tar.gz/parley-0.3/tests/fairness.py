# Miscellaneous tests (work in progress)

from parley import *

import framework as test

# TODO: this raises NoSuchActor when in thread mode
def a():
    other = spawn_link(b, me())
    while True:
        if recv() != 'hello!':
            break
        other.send('hello!', me())

def b(other):
    while True:
        other.send('hello!', me())
        if recv() != 'hello!':
            break

@test.good
def main():
    trace_on()
    spawn_link(a)
    for i in range(50):
        #print 'still going'
        schedule()
    print me(), 'quitting'


def ping2():
    other = spawn_link(pong2, me())
    while True:
        recv()
        other.send('hello from ping!', me())

def pong2(other):
    while True:
        other.send('hello from pong!', me())
        recv()

# In tasklet mode, this test case is detected as a deadlock when using
# ChannelWrapper but not when using WackyChannelWrapper.
@test.ugly
def main2():
    spawn_link(ping2)
    for i in range(10):
        schedule()



if __name__=='__main__':
    model = sys.argv[1]
    fn_name = sys.argv[2]
    fn = globals()[fn_name]
    if model == 'thread':
        start_thread_controller(fn)
    elif model == 'tasklet':
        start_tasklet_controller(fn)
    elif model == 'greenlet':
        start_greenlet_controller(fn)
    else:
        raise ValueError('Unknown execution model: ' + model)
