from distutils.core import setup

setup(name='parley',
      description='Python Actor Runtime LibrarY',
      author='Jacob Lee',
      author_email='artdent@freeshell.org',
      url='http://osl.cs.uiuc.edu/parley/',
      version='0.1',
      packages=['parley', 'parley.controllers'],
      data_files=[('demo', 'demo/'),
                  ('', ['README', 'INSTALL', 'LICENSE'])],
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
