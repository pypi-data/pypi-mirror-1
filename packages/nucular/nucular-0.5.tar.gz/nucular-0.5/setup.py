
long_description = """
Nucular is a system for creating full text indices for fielded data.
It can be accessed via a Python API or via a suite of command line interfaces.

Nucular archives fielded documents and retrieves them based on field value,
field prefix, field word prefix, or full text word prefix, word proximity or
combinations of these. Nucular also includes features for determining values
related to a query often called query facets.

Features

Nucular is very light weight. Updates and accesses do not require any
server process or other system support such as shared memory locking.

Nucular supports concurrency. Arbitrary concurrent updates and accesses
by multiple processes or threads are supported, with no possible locking issues.

Nucular is pure Python.
Nucular indexes and retrieves data quickly.
Nucular has a funny name.

More information about nucular including links to documentation,
and releases is available at http://nucular.sourceforge.net .
"""

from distutils.core import setup
import sys

if sys.version<"2.3":
    raise ValueError, "requires python 2.3 or better"

setup(name="nucular",
      version="0.5",
      description="nucular fielded text indexing and retrieval",
      long_description = long_description,
      author="Aaron Watters",
      author_email="aaron_watters@sourceforge.net",
      url="http://nucular.sourceforge.net/",
      packages=['nucular', 'nucular.frames'],
      license="BSD",
      keywords="search index text",
      scripts = [
          'scripts/nucularAggregate.py',
          'scripts/nucularDump.py',
          'scripts/nucularLoad.py',
          'scripts/nucularSite.py',
          'scripts/nucularQuery.py',
          ],
      classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.5",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Indexing",
    ],
     )

