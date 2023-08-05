from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.1'

setup(name='simpleQL',
      version=version,
      description="Efficient filtering of SQL tables with generator expressions.",
      long_description="""\
This module allows you to access a (DB API 2) SQL table using nothing
but Python to build the query::

    >>> from pysqlite2 import dbapi2 as sqlite
    >>> conn = sqlite.connect("coastline.db")
    >>> from simpleql.table import Table
    >>> table = Table(conn, "coastline", verbose=True)
    >>> print table
    {'longitude': <simpleql.table.Col object at 0x547070>, 'latitude': <simpleql.table.Col object at 0x547050>}
    >>> for row in (r for r in table if r.latitude > 83 and (r.longitude < 300 or r.longitude > 320)):
    ...     print row
    SELECT longitude, latitude FROM coastline WHERE (latitude>83) AND ((longitude<300) OR (longitude>320));
    {'longitude': 292.53553099999999, 'latitude': 83.016946000000004}
    {'longitude': 292.188199, 'latitude': 83.019293000000005}
    {'longitude': 290.23328500000002, 'latitude': 83.019293000000005}
    {'longitude': 289.97044, 'latitude': 83.031026999999995}
    {'longitude': 289.65127000000001, 'latitude': 83.014599000000004}
    <snip>

As you can see, the query string is built from a generator expression.
You can also use list comprehensions. Regular expressions are
supported by the use of the
``re.search`` method::

    >>> table = Table(conn, "table")
    >>> filtered = (r for r in table if re.search("string", r['column']))
    >>> for row in filtered:
    ...     print row
    SELECT column FROM table WHERE column LIKE "%string%";
    <snip>

The advantage of this approach over the `similar recipe
<http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/442447>`_ is
that if the (efficient) query builder fails when it encounters a
complex filter the data will still be filtered (unefficiently) by
the generator expression.
""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='sql pythonic',
      author='Roberto De Almeida',
      author_email='roberto@dealmeida.net',
      url='http://dealmeida.net/projects/simpleql',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
      
