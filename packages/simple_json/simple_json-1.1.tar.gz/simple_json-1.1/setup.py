#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

VERSION = '1.1'
DESCRIPTION = "Compatibility shim for simplejson"
LONG_DESCRIPTION = """
simple_json was renamed to simplejson to comply with PEP 8 module naming
conventions.  This package allows existing installations to work.
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
    install_requires=['simplejson'],
    packages=find_packages(exclude=['ez_setup']),
    platforms=['any'],
    zip_safe=True,
)
