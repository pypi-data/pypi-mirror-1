'''
bugs.py - various actor systems that are supposed to succeed, fail, or timeout.

Use "runner.py bugs" to test this file.
'''

import sys

from parley import *
from parley.helpers import function_actor, forward_exceptions

import framework as test

# Sample actor that succeeds
@function_actor
def good_actor(a, b):
    set_name('good')
    return a + b

# Sample actor that throws an exception in response to any message
@function_actor
def bad_actor(a, b):
    set_name('bad')
    raise RemoteException(ValueError)

# Sample actor that also throws an exception
@function_actor
@forward_exceptions([ValueError])
def bad_actor2(a, b):
    set_name('bad2')
    raise ValueError

# Sample actor that hangs around forever
@function_actor
def ugly_actor(a, b):
    set_name('ugly')
    while True:
        recv()

# Sample actor that throws a message right away
def very_bad_actor():
    set_name('very_bad')
    raise Exception('I am a very bad actor')

@test.good
def test_good_link():
    def _test_good_link():
        a = spawn_link(good_actor)
        assert a.add(2, 3) == 5
    spawn(_test_good_link)

@test.good
def test_good_link_in_main():
    import time
    a = spawn_link(good_actor)
    a.add(2, 3)

@test.bad
def test_bad_link():
    def _test_bad_link():
        a = spawn_link(bad_actor)
        a.add(2, 3)
    spawn(_test_bad_link)

@test.bad
def test_bad_link_in_main():
    a = spawn_link(bad_actor)
    a.add(2, 3)

@test.bad
def test_forward_exceptions():
    a = spawn_link(bad_actor2)
    a.add(2, 3)

@test.ugly
def test_ugly_link():
    def _test_ugly_link():
        a = spawn_link(ugly_actor)
        a.add(2, 3)
    spawn(_test_ugly_link)

@test.ugly
def test_ugly_link_in_main():
    a = spawn_link(ugly_actor)
    a.add(2, 3)

@test.good
def test_good_manual_link():
    a = spawn(good_actor)
    a.add(2,3)
    a.quit()

@test.ugly
def test_bad_nolink_call():
    a = spawn(bad_actor)
    a.add(2,3)

@test.good
def test_good_nolink_call_quit():
    a = spawn(good_actor)
    a.add(2,3)
    a.quit()

@test.good
def test_bad_nolink_send():
    a = spawn(bad_actor)
    a.send('add', me(), 2, 3)
    print recv()
    a.quit()

@test.ugly
def test_good_nolink():
    a = spawn(good_actor)
    for i in range(10):
        print a.add(i, i+2)

@test.good
def test_recv_nowait():
    a = spawn_link(ugly_actor)
    assert recv_nowait() is None

@test.good
def test_recv_nowait2():
    a = spawn_link(good_actor)
    a.send('add', me(), 2, 3)
    while recv_nowait() is None:
        pass

@test.good
def test_become():
    import sys
    sys.setrecursionlimit(100)
    
    def counter(n):
        if n > 0:
            become(counter, n-1)
    counter(200)

@test.good
def test_sysexit():
    sys.exit()

@test.good
def test_sysexit2():
    spawn(ugly_actor)
    sys.exit()

@test.good
def test_sysexit3():
    def quit():
        sys.exit()
    spawn(quit)
    recv()

@test.good
def test_sysexit4():
    def quit():
        sys.exit()
    spawn_link(quit)
    recv()

# Test that schedule() yields and listens for signals
@test.bad
def test_schedule():
    a = spawn_link(very_bad_actor)
    while True:
        schedule()

@test.good
def test_schedule2():
    def do_nothing():
        while True:
            schedule()
    a = spawn(do_nothing)
    sys.exit()

@test.bad
def test_schedule3():
    a = spawn_link(bad_actor)
    a.send('foo')
    while True:
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
