#!/usr/bin/env python

from distutils.core import setup

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

long_description = """
NonMockObjects
==============

NonMockObjects aims to make it easy to create complicated structures
representing more realistic test data, thus allowing you to write
tests against your *real* code, not mock objects. This allows you to
write high-level integration tests almost as easily as small-scale
unit tests, once you build up your library of creation functions.

**How to tell if you need this module**: You want to run automated
tests on your code, but you have a relatively complicated data model,
perhaps a nicely normalized database. The bulk of your tests consist
of setting up this relatively complicated data model, and the tests
all break whenever you change your model. Constructing the data has
become so difficult (and breaks so often) that you've just stopped
testing entirely.
"""

setup(name='NonMockObjects',
      version='0.1.0',
      description='A module for easily creating more realistic test data',
      long_description = long_description,
      author='Jeremy Bowers',
      author_email='jerf@jerf.org',
      url='http://www.jerf.org/programming/nonMockObjects.html',
      py_modules=['nonmockobjects'],
      package_dir={'': 'src'},
      classifiers=['Topic :: Software Development :: Testing',
                   'Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: Public Domain',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python']
     )

