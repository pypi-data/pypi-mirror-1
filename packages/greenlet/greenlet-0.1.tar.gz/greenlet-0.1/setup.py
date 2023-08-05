#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension

VERSION = '0.1'
DESCRIPTION = 'Lightweight in-process concurrent programming'
LONG_DESCRIPTION = """
(This is the py.magic.greenlet module from the py lib
<http://codespeak.net/py/>)

The "greenlet" package is a spin-off of Stackless, a version of CPython that
supports micro-threads called "tasklets".  Tasklets run pseudo-concurrently
(typically in a single or a few OS-level threads) and are synchronized with
data exchanges on "channels".

A "greenlet", on the other hand, is a still more primitive notion of
micro-thread with no implicit scheduling; coroutines, in other words.
This is useful when you want to control exactly when your code runs.
You can build custom scheduled micro-threads on top of greenlet; however, it
seems that greenlets are useful on their own as a way to make advanced control
flow structures.  For example, we can recreate generators; the difference with
Python's own generators is that our generators can call nested functions and
the nested functions can yield values too.  Additionally, you don't need a
"yield" keyword. See the example in test_generator.py.

Greenlets are provided as a C extension module for the regular unmodified
interpreter.
"""

CLASSIFIERS = filter(None, map(str.strip,
"""                 
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Natural Language :: English
Programming Language :: Python
Operating System :: OS Independent
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines()))

REPOSITORY="http://svn.red-bean.com/bob/greenlet/trunk/"

setup(
    name="greenlet",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    maintainer="Bob Ippolito",
    maintainer_email="bob@redivi.com",
    url="http://undefined.org/python/#greenlet",
    license="MIT License",
    platforms=['any'],
    test_suite='nose.collector',
    download_url=REPOSITORY + "#egg=greenlet-dev",
    ext_modules=[Extension(name='greenlet', sources=['greenlet.c'])],
)
