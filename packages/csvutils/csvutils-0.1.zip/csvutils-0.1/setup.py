#!/usr/bin/env python

from distutils.core import setup

setup(
    name            = 'csvutils',
    version         = '0.1',
    py_modules      = ['csvutils'],
    author          = 'George Sakkis',
    author_email    = 'george.sakkis@gmail.com',
    description     = 'Transformation utilities for csv (or csv-like) generated rows',
    long_description=
'''The standard csv module is very useful for parsing tabular data in CSV format.
Typically though, one or more transformations need to be applied to the generated
rows before being ready to be used; for instance "convert the 3rd column to int,
the 5th to float and ignore all the rest". This module provides an easy way to
specify such transformations upfront instead of coding them every time by hand.

Two classes are currently available, SequenceTransformer and MappingTransformer,
that represent each row as a list (like csv.reader) or dict (like csv.DictReader),
respectively.
''',
    classifiers     = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
	'Topic :: Utilities',
        'Topic :: Text Processing :: General',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
