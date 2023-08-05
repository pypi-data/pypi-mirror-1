Introduction
------------

The sqltriples package provides an RDF triple store residing in an
SQL-accessible database system with an API similar to that provided by rdflib.

Quick Start
-----------

First, set up the database for use as a triple store, specifying a database
name, database module and the argument requesting the initialisation of the
store.

PYTHONPATH=. python tools/sqltriples_admin.py --database=testdb \
  --module=pysqlite2 --init

(Choose PgSQL instead of pysqlite2 in order to make use of PostgreSQL
databases.)

To test the triple store, run the test program:

PYTHONPATH=. python test.py --database=testdb --module=pysqlite2

The --table-name and --sequence-name arguments can be used to choose different
database objects than those chosen by default:

PYTHONPATH=. python tools/sqltriples_admin.py --database=testdb \
  --module=PgSQL --table-name=mytriples --sequence-name=mysequence --init

(The sequence name is not actually used by pysqlite2.)

It can be interesting to start Python in interactive mode and to manipulate
the store interactively:

PYTHONPATH=. python -i test.py --database=testdb --module=pysqlite2 --no-test

This gives the opportunity to examine and use the store object, 's':

>>> s
<sqltriples.TripleStore instance at 0xb7b5496c>
>>> s.triples((None, None, None))
[]

To see the statements being sent to the database system, the --debug argument
can be given to the test and administration programs, or the 'debug' attribute
can be set to a true value on store objects.

Contact, Copyright and Licence Information
------------------------------------------

The current Web page for sqltriples at the time of release is:

http://www.boddie.org.uk/python/sqltriples.html

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/LICENCE.txt for more information.

Dependencies
------------

sqltriples has the following basic dependencies:

Package                     Release Information
-------                     -------------------

pyPgSQL                     Tested with 2.4.0 (using PostgreSQL 7.4.7)
pysqlite2                   Tested with 2.1.3 (using sqlite 3.2.8)
CMDsyntax                   Tested with 0.91

One can choose between the above dependencies, and it is possible that more
database systems will eventually be supported.

URLs
----

Dependencies:

pyPgSQL                     http://pypgsql.sourceforge.net/
PostgreSQL                  http://www.postgresql.org/
pysqlite2                   http://pysqlite.org/
sqlite                      http://www.sqlite.org/
CMDsyntax                   http://www.boddie.org.uk/david/Projects/Python/CMDSyntax/index.html

For reference:

rdflib                      http://rdflib.net/

New in sqltriples 0.3.1 (Changes since sqltriples 0.3)
------------------------------------------------------

  * Fixed handling of empty list values in patterns: these should inhibit
    result production.

New in sqltriples 0.3 (Changes since sqltriples 0.2.1)
------------------------------------------------------

  * Made sqltriples a proper Python package.
  * Made significant changes to query construction, introducing additional
    features (eg. tuples) and store methods (such as those for conjunction,
    disjunction and negation). Added partial retrieval (where queries
    involving n-tuples may return shorter tuples) and subject ordering
    support.
  * Added various node classes as attributes to the store, along with other
    conveniences.
  * Added index creation in the database for potential performance
    improvements.

New in sqltriples 0.2.1 (Changes since sqltriples 0.2)
------------------------------------------------------

  * Changed the Namespace class to inherit from URIRef.
  * Introduced helper classes for expressions, along with classes to describe
    conjunctions, disjunctions, unions and intersections.
  * Fixed subquery membership in cases where functions are applied to object
    values.
  * Added a pattern parameter to the subjects and predicates methods in order
    to expose more advanced querying.
  * Added support for testing against lists of predicates.
  * Added support for negated queries, the presence of values in triples (and
    other results), and for particular object types in expressions.

New in sqltriples 0.2 (Changes since sqltriples 0.1)
----------------------------------------------------

  * Changed the querying mechanisms to use the SQL "exists" keyword with
    subqueries/subselects, rather than testing for the presence of result
    tuples in subqueries.
  * Moved the test code into a separate program.
  * Added support for pysqlite2, introducing adapters for database systems.
  * Added support for filtering functions, exposed only in the objects method,
    currently.
  * Changed the open function to require either a database name and a module
    name or an adapter object, created using the provided adapter classes.
    Where a configuration is not supported, NotSupportedError exceptions are
    raised.

Release Procedures
------------------

Update the sqltriples/__init__.py __version__ attributes.
Change the version number and package filename/directory in the documentation.
Change code examples in the documentation if appropriate.
Update the release notes (see above).
Check the setup.py file and ensure that all package directories are mentioned.
Check the release information in the PKG-INFO file and in the package
changelog (and other files).
Tag, export.
Generate the API documentation.
Remove generated .pyc files: rm `find . -name "*.pyc"`
Archive, upload.
Upload the introductory documentation.
Update PyPI entry.

Generating the API Documentation
--------------------------------

In order to prepare the API documentation, it is necessary to generate some
Web pages from the Python source code. For this, the epydoc application must
be available on your system. Then, inside the distribution directory, run the
apidocs.sh tool script as follows:

./tools/apidocs.sh

Some warnings may be generated by the script, but the result should be a new
apidocs directory within the distribution directory.

Making Packages
---------------

To make Debian-based packages:

  1. Create new package directories under packages if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/ubuntu-hoary/python2.4-sqltriples/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
