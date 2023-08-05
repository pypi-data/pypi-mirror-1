from distutils.core import setup

version='0.2'

long_desc = '''
PARLEY is an API for writing Python programs that implement the Actor
model of distributed systems, in which lightweight concurrent
processes communicate through asynchronous message-passing. Actor
systems typically are easier to write and debug than traditional
concurrent programs that use locks and shared memory.

PARLEY can run using either traditional native threads or user-space
threads (i.e. the "tasklets" implemented by Stackless Python). A
program written using PARLEY can choose between the two by changing
a single line of code.
'''

setup(name='parley',
      description='Python Actor Runtime LibrarY',
      long_description=long_desc,
      author='Jacob Lee',
      author_email='artdent@freeshell.org',
      url='http://osl.cs.uiuc.edu/parley/',
      version=version,
      license='Lesser General Public License',
      packages=['parley', 'parley.controllers'],
      platforms=['any'],
      classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules'
    ]
      )
