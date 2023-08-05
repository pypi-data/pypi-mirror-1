'''
bugs.py - various actor systems that are supposed to succeed, fail, or timeout.

Use "runner.py bugs" to test this file.
'''

from parley import *
from parley.helpers import function_actor, forward_exceptions
import py.test

good_fns = []
bad_fns = []
ugly_fns = []

def good(fn): # succeeds => good
    good_fns.append(fn.__name__)
    return fn
def bad(fn): # prints to stderr => bad
    bad_fns.append(fn.__name__)
    return fn
def ugly(fn): # runs forever => ugly
    ugly_fns.append(fn.__name__)
    return fn

# Sample actor that succeeds
@function_actor
def good_actor(a, b):
    return a + b

# Sample actor that throws an exception
@function_actor
def bad_actor(a, b):
    raise RemoteException(ValueError)

# Sample actor that also throws an exception
@function_actor
@forward_exceptions([ValueError])
def bad_actor2(a, b):
    raise ValueError

# Sample actor that hangs around forever
@function_actor
def ugly_actor(a, b):
    while True:
        recv()


@good
def test_good_link():
    def _test_good_link():
        a = spawn_link(good_actor)
        assert a.add(2, 3) == 5
    spawn(_test_good_link)

@good
def test_good_link_in_main():
    import time
    a = spawn_link(good_actor)
    a.add(2, 3)

@bad
def test_bad_link():
    def _test_bad_link():
        a = spawn_link(bad_actor)
        a.add(2, 3)
    spawn(_test_bad_link)

@bad
def test_bad_link_in_main():
    a = spawn_link(bad_actor)
    a.add(2, 3)

@bad
def test_forward_exceptions():
    a = spawn_link(bad_actor2)
    a.add(2, 3)

@ugly
def test_ugly_link():
    def _test_ugly_link():
        a = spawn_link(ugly_actor)
        a.add(2, 3)
    spawn(_test_ugly_link)

@ugly
def test_ugly_link_in_main():
    a = spawn_link(ugly_actor)
    a.add(2, 3)

@good
def test_good_manual_link():
    a = spawn(good_actor)
    a.add(2,3)
    a.quit()

@ugly
def test_bad_nolink_call():
    a = spawn(bad_actor)
    a.add(2,3)

@good
def test_good_nolink_call_quit():
    a = spawn(good_actor)
    a.add(2,3)
    a.quit()

@good
def test_bad_nolink_send():
    a = spawn(bad_actor)
    a.send('add', me(), 2, 3)
    print recv()
    a.quit()

@ugly
def test_good_nolink():
    a = spawn(good_actor)
    for i in range(10):
        print a.add(i, i+2)

@good
def test_recv_nowait():
    a = spawn_link(ugly_actor)
    assert recv_nowait() is None

@good
def test_recv_nowait2():
    a = spawn_link(good_actor)
    a.send('add', me(), 2, 3)
    while recv_nowait() is None:
        pass

if __name__=='__main__':
    model = sys.argv[1]
    fn_name = sys.argv[2]
    fn = globals()[fn_name]
    if model == 'thread':
        start_thread_controller(fn)
    else:
        start_tasklet_controller(fn)
