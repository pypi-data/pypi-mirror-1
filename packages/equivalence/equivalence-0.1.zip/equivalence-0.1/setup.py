#!/usr/bin/env python

from distutils.core import setup

setup(
    name            = 'equivalence',
    version         = '0.1',
    py_modules      = ['equivalence', 'test_equivalence'],
    author          = 'George Sakkis',
    author_email    = 'george.sakkis@gmail.com',
    description     = 'Ad-hoc and key-based equivalence relations',
    long_description=
'''The ``Equivalence`` class can be used to maintain a partition of objects
into equivalence sets, making sure that the equivalence properties (reflexivity,
symmetry, transitivity) are maintained. Two objects ``x`` and ``y`` are
considered equivalent either implicitly (through a key function) or explicitly by
calling ``merge(x,y)``.
''',
    classifiers     = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
