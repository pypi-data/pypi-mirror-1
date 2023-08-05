#!/usr/bin/python

'''
runner.py - parley test utility

This utility handles a very specific kind of test:
whether a given program succeeds (good), fails (bad), or hangs (ugly).
Failure is defined as printing anything to stderr;
hanging is defined as exceeding a timeout (default = 1s).

Running "runner.py <module>" will import the given module and
examine module.good_fns, module.bad_fns, and module.ugly_fns to find a list of
function names that are expected to succeed, fail, and time out, respectively.
Rather than calling these functions directly, runner.py invokes the module
as a subprocess, passing it a command line consisting of a threading model
to use ("tasklet" or "thread") and the function to invoke.

See bugs.py for a sample module that is callable by this utility.
'''

import subprocess
import time
import sys
import os
import signal

python_path = 'python-stackless'
#module_path = '/home/jacob/parley/tags/0.1.1'
timeout = 1

class Result:
    SUCCESS = 'success'
    EXCEPTION = 'exception'
    TIMEOUT = 'timeout'

def run_command(script, *args):
    #env = {}
    #if module_path:
    #    env['PYTHONPATH'] = module_path
    cmd = [python_path, script] + list(args)
    print 'running', ' '.join(cmd), '...',
    sys.stdout.flush()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    timed_out = False
    dt = .1
    start = time.time()
    while p.poll() == None:
        time.sleep(dt)
        dt += .1
        if time.time() - start > timeout:
            print 'timeout'
            os.kill(p.pid, signal.SIGTERM)
            return Result.TIMEOUT, p.stdout.read(), p.stderr.read()

    stderr = p.stderr.read()
    stdout = p.stdout.read()
    if len(stderr) > 0:
        print 'exception'
        return Result.EXCEPTION, stdout, stderr
    else:
        print 'success'
        return Result.SUCCESS, stdout, stderr


def read_config(path):
    cases = []
    for line in open(path):
        args = line.split()
        path = args.pop(0)
        expected_result = args.pop(-1)
        cases.append((path, args, expected_result))
    return cases

expected_outcome = dict(
    good=Result.SUCCESS,
    bad=Result.EXCEPTION,
    ugly=Result.TIMEOUT
    )

def log_failure(name, model, ret, behavior, stdout, stderr):
    print '-'*40
    print 'Failed test: %s %s (result=%s, expected %s)' % (
        name, model, ret, expected_outcome[behavior])
    print 'STDOUT'
    print '--'
    print stdout
    print 'STDERR'
    print '--'
    print stderr
    

def main(module):
    m = __import__(module)
    
    success = 0
    failure = 0
    tasklet_failures = []
    thread_failures = []
    tests = [(behavior, model, fn)
             for model in ('tasklet', 'thread')
             for behavior in ('good', 'bad', 'ugly')
             for fn in getattr(m, behavior + '_fns')]
    for behavior, model, fn in tests:
        ret, stdout, stderr = run_command(module + '.py', model, fn)
        if ret == expected_outcome[behavior]:
            success += 1
        else:
            failure += 1
            if model == 'tasklet':
                tasklet_failures.append(fn)
            else:
                thread_failures.append(fn)
            log_failure(fn, model, ret, behavior, stdout, stderr)
    print 'success: %d, failure: %d' % (success, failure)
    
    tasklet_failures.sort()
    thread_failures.sort()
    print 'tasklet failures:'
    print '\n'.join('\t' + name for name in tasklet_failures)
    print 'thread failures:'
    print '\n'.join('\t' + name for name in thread_failures)

if __name__=='__main__':
    main(sys.argv[1])
    
