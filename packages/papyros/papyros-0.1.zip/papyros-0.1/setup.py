#!/usr/bin/env python

from distutils.core import setup

setup(
    name            = 'papyros',
    version         = '0.1',
    packages        = ['papyros'],
    package_data    = {'papyros' : ['logging.conf']},
    author          = 'George Sakkis',
    author_email    = 'george.sakkis@gmail.com',
    url             = 'http://code.google.com/p/papyros/',
    download_url    = 'http://papyros.googlecode.com/files/papyros-0.1.zip',
    description     = 'Lightweight master-slave parallel processing package',
    long_description=
'''Papyros is a small platform independent parallel processing Python package,
providing a master-slave model. Clients can submit jobs to a master object which
is monitored by one or more slave objects that do the real work. Two main
implementations are provided, one using multiple threads and one multiple
processes in one or more hosts (through [http://pyro.sourceforge.net/ Pyro]).
The primary design goal is simplicity: a user can replace a time consuming loop
in a single-thread single-process program with the equivalent parallel version
in a few lines of code, with minimal boilerplate overhead.
''',
    classifiers     = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Distributed Computing',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
