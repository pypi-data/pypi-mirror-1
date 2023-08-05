'''
adders.py - two basic examples of actor interaction.
'''

from parley import *
from parley.helpers import function_actor

def adder():
    while True:
        msg, sender, args, kwargs = recv()
        if msg == 'quit':
            break
        else:
            ret = args[0] + args[1]
            sender.send('reply', me(), ret)

@function_actor
def adder2(op1, op2):
    return op1 + op2

def main():
    a = spawn_link(adder2)
    for i in range(10):
        print a.add(i, i+2)
    a.quit()

if __name__=='__main__':
    start_thread_controller()
    spawn(main)
