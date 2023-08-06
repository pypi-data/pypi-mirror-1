#!/usr/bin/python

import os
from distutils.core import setup
import simpleopt

if os.stat('simpleopt.py').st_mtime > os.stat('README').st_mtime:
    file('README','w').write(simpleopt.__doc__)

setup(
    name = 'simpleopt',
    version = simpleopt.__version__,
    description = simpleopt.__doc__.splitlines()[0],
    long_description = simpleopt.__doc__,
    maintainer = simpleopt.__author__,
    maintainer_email = simpleopt.__author_email__,
    #url = 'http://qubit.ic.unicamp.br/~nilton',
    py_modules = ['simpleopt', 'odict'],
    classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: User Interfaces',
    'Topic :: Terminals',
    ],
)
