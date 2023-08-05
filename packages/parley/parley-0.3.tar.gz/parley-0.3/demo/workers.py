'''
workers.py - another basic example of actor communication.
'''

from parley import *
from parley.helpers import forward_exceptions

import operator

@forward_exceptions([AttributeError])
def worker():
    while True:
        op_name, requester, args, kwargs = recv()
        if op_name == 'quit':
            break
        ret = getattr(operator, op_name)(*args)
        requester.send('reply', me(), ret)

def main(num_workers):
    workers = [spawn_link(worker) for i in range(num_workers)]
    ops = ['add', 'sub', 'mod']
    for i in range(20):
        op = ops[i%len(ops)]
        print '%d %s %d: %d' % (i**2, op, i,
                                workers[i%num_workers].call(op, me(), i**2, i))
    # Since we spawned the workers using spawn_link,
    # workers will implicitly receive a 'quit' message from main
    # at this point in the program.

if __name__=='__main__':
    start_thread_controller(main, 5)

