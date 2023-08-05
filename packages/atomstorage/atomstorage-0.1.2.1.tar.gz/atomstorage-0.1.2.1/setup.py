from setuptools import setup, find_packages
import sys, os

version = '0.1.2.1'

setup(name='atomstorage',
      version=version,
      description="API for storing and retrieving Atom entries.",
      long_description="""
This module defines a simple API for storing and retrieving Atom
entries in different storage backends. Entries are defined using a
JSON-like syntax::

    >>> import datetime
    >>> entry = {'id'     : 'http://example.com/1',
    ...          'title'  : 'My first entry',
    ...          'updated': datetime.datetime.utcnow(),
    ...         }

The module comes with a shelve backend::

    >>> from atomstorage import EntryManager
    >>> em = EntryManager('shelve://file.db')
    >>> em.create_entry(entry)
    {'updated': datetime.datetime(2006, 8, 15, 16, 27, 7, 960677),
     'id': 'http://example.com/1',
     'title': 'My first entry'}

New backends can be easily added by creating a module and setting
an `atomstorage.backend` entry point. A SQLite backend is currently
being developed.

The API defines a few methods the entry manager should have. To
retrieve all entries, sorted by time (last to first)::

    >>> entries = em.get_entries()

The last 10 entries::

    >>> entries = em.get_entries(10) 

Retrieve the entry with id "1"::

    >>> entry = em.get_entry("1") 

Delete the same entry::

    >>> em.delete_entry("1")

Get all entries from August 2006::

    >>> entries = em.get_entries_by_date(2006, 8)

Or from the "tech" category::
    
    >>> entries = em.get_entries_by_category("tech")

To search for entries mentioning "Python"::

    >>> entries = em.search("Python") 

The API is by no means final. Comments, suggestions, patches and
critics are welcome.
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Roberto De Almeida',
      author_email='roberto@dealmeida.net',
      url='http://dealmeida.net/projects/atomstorage',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'pickleshare': ["pickleshare"],
      },
      entry_points="""
      # -*- Entry points: -*-
      [atomstorage.backend]
      shelve = atomstorage.shelvestorage:EntryManager
      pickleshare = atomstorage.picklesharestorage:EntryManager
      """,
      )
      
