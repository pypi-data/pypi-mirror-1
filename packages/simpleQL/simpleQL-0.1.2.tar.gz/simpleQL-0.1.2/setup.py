from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Database :: Front-Ends
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.1.2'

setup(name='simpleQL',
      version=version,
      description="Efficient filtering of SQL tables with generator expressions.",
      long_description="""\
This module allows you to access a (DB API 2) SQL table using nothing
but Python to build the query::

    >>> import re
    >>> from pysqlite2 import dbapi2 as sqlite
    >>> from simpleql.table import Table

    >>> conn = sqlite.connect(":memory:")
    >>> curs = conn.cursor()
    >>> curs.execute("CREATE TABLE test (a integer, b char(1))")
    >>> curs.executemany("INSERT INTO test (a, b) VALUES (?, ?)", ([1,'a'], [2,'b'], [3,'c']))
    >>> conn.commit()

    >>> table = Table(conn, "test", verbose=1)
    >>> for row in table:
    ...     print row
    ...
    SELECT a, b FROM test;
    {'a': 1, 'b': u'a'}
    {'a': 2, 'b': u'b'}
    {'a': 3, 'b': u'c'}

    >>> aspan = (1, 3)
    >>> for row in (t for t in table if min(aspan) < t.a < max(aspan)):
    ...     print row
    ... 
    SELECT a, b FROM test WHERE (1<a) AND (a<3);
    {'a': 2, 'b': u'b'}

(This is a *fake* example, the filtering does not work in interactive
mode.)

As you can see, the query string is built from a generator expression.
You can also use list comprehensions. Regular expressions are
supported by the use of the
``re.search`` method::

    >>> filtered = [t for t in table if re.search('a', t.b)]
    SELECT a, b FROM test WHERE b LIKE "%a%";
    >>> print filtered
    [{'a': 1, 'b': u'a'}]

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
      
