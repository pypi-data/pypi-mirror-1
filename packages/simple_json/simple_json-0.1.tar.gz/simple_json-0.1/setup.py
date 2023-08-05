#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension

VERSION = '0.1'
DESCRIPTION = "Simple, fast, extensible JSON encoder for Python"
LONG_DESCRIPTION = """
simple_json is a simple, fast, and extensible JSON encoder for Python.

It may be subclassed to provide serialization in any kind of situation,
without any special support by the objects to be serialized (somewhat
like pickle).
"""

CLASSIFIERS = filter(None, map(str.strip,
"""                 
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines()))

setup(
    name="simple_json",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    author="Bob Ippolito",
    author_email="bob@redivi.com",
    url="http://undefined.org/python/#simple_json",
    license="MIT License",
    packages=['simple_json'],
    platforms=['any'],
    zip_safe=True,
)
