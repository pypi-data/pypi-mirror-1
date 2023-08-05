from distutils.core import setup

version='0.3'

long_desc = """
PARLEY is a library for writing Python programs that implement the Actor
model of distributed systems, in which lightweight concurrent
processes communicate through asynchronous message-passing. Actor
systems typically are easier to write and debug than traditional
concurrent programs that use locks and shared memory.

PARLEY can run using either traditional native threads, greenlets
(lightweight threads), or Stackless Python's tasklets. A program
written using PARLEY can choose between these models by changing a
single line of code.
"""

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
