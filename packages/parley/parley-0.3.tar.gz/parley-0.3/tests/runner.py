#!/usr/bin/python

'''
runner.py - parley test utility

Usage: runner.py <module> [list of execution models]

This utility handles a very specific kind of test: whether a given
program succeeds (good), fails (bad), or hangs (ugly).  Failure is
defined as printing anything to stderr; hanging is defined as
exceeding a timeout (default = 1s).

Running "runner.py <module>" will import the given module and examine
module.good_fns, module.bad_fns, and module.ugly_fns to find a list of
function names that are expected to succeed, fail, and time out,
respectively.  Rather than calling these functions directly, runner.py
invokes the module as a subprocess, passing it a command line
consisting of an execution model to use ("tasklet", "thread", or
"generator") and the function to invoke.

Any additional parameters identify execution models to test: for
example, "runner.py foo greenlet thread" will test the foo module
under the greenlet and thread execution models. If no models are
specified, all models are tested.

See bugs.py for a sample module that is callable by this utility.
'''

import subprocess
import time
import sys
import os
import signal

import framework

python_path = 'python-stackless'
#module_path = '/home/jacob/parley/tags/0.1.1'
timeout = 1
all_models = 'tasklet', 'thread', 'greenlet'

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
    

def main(module, models):
    if len(models) == 0:
        models = all_models
    
    m = __import__(module)
    
    success = 0
    failure = 0
    failures = {}
    for model in models:
        failures[model] = []
    tests = [(behavior, model, fn)
             for model in models
             for behavior in ('good', 'bad', 'ugly')
             for fn in getattr(framework, behavior + '_fns')]
    for behavior, model, fn in tests:
        ret, stdout, stderr = run_command(module + '.py', model, fn)
        if ret == expected_outcome[behavior]:
            success += 1
        else:
            failure += 1
            failures[model].append(fn)
            log_failure(fn, model, ret, behavior, stdout, stderr)
    print 'success: %d, failure: %d' % (success, failure)

    for model, failed_tests in failures.items():
        failed_tests.sort()
        print model, 'failures:'
        print '\n'.join('\t' + name for name in failed_tests)

if __name__=='__main__':
    main(sys.argv[1], sys.argv[2:])
    
