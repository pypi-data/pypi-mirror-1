#!/usr/bin/env python
# Setup script for ezpyinline

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

classifiers = """\
Development Status :: 2 - Pre-Alpha
Intended Audience :: Developers
License :: OSI Approved :: Artistic License
Programming Language :: Python
Operating System :: OS Independent
Natural Language :: English
Topic :: Software Development :: Build Tools
"""

import ezpyinline

setup (name = "ezpyinline",
       version = "0.1",
       description = "Easy embedded Inline C for Python",
       author = "__tim__",
       author_email = "timchen119@gmail.com",
       maintainer = "__tim__",
       maintainer_email = 'timchen119@gmail.com',
       url = "http://ezpyinline.sf.net",
       license = "Artistic",
       platforms = "any",
       classifiers = filter(None, classifiers.split("\n")),
       long_description = ezpyinline.__doc__,
       py_modules = ['ezpyinline'],
      )
