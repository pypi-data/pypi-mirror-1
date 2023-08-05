#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
A simple SQL-accessible RDF triple store.

Copyright (C) 2006 Paul Boddie <paul@boddie.org.uk>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

--------

To initialise the database, use the init method on the TripleStore object as
follows:

from sqltriples import TripleStore
store = TripleStore(connection, "triples") # "triples" is the default, anyway
store.init()
store.commit()

See the _init_table and _init_sequence attributes on the TripleStore class for
details of the table and sequence employed.

To remove the triple store objects from the database, use the delete method on
the TripleStore object as follows:

store.delete()
store.commit()

See the _delete_table and _delete_sequence attributes on the TripleStore class
for details.

NOTE: The statements sent to the database system can be configured, but this
NOTE: should be made convenient in future releases.
"""

__version__ = "0.1"

from pyPgSQL import PgSQL
import sys

# Special data types.
# These inherit from the unicode type in order to provide interoperability
# with rdflib.

class Special(unicode):
    def __repr__(self):
        return "%s: %s" % (self.__class__.__name__, self)

class URIRef(Special):
    pass

class Literal(Special):
    pass

class Namespace(Special):
    def __getitem__(self, item):
        try:
            return unicode(self)[item]
        except TypeError:
            return Namespace(self + item)

class BNode:
    def __init__(self, value=None):
        self.value = value
    def __repr__(self):
        return "%s: %s" % (self.__class__.__name__, self.value)
    def __unicode__(self):
        return self.value
    def __eq__(self, other):
        return hasattr(other, "value") and self.value == other.value
    def __hash__(self):
        # NOTE: Should probably be more careful to avoid collisions with non-BNodes.
        return hash(self.value)

# Useful defaults.

RDFNS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
TYPE = RDFNS["type"]

# Store-related classes.

class TripleStore:

    """
    A triple store whose contents are stored in an SQL-accessible database
    table.
    """

    # Conversions for storage.

    names_to_codes = {
        "URIRef" : "U",
        "Literal" : "L",
        "BNode" : "B",
        "Namespace" : "U"
        }

    codes_to_names = {
        "U" : "URIRef",
        "L" : "Literal",
        "B" : "BNode"
        }

    # A table indicating whether a paramstyle mandates a dictionary when values
    # are being presented to the database system.

    paramdict = {
        "qmark" : 0, "numeric" : 0, "named" : 1, "format" : 0, "pyformat" : 1
        }

    # Database-specific statements.
    # NOTE: Needs generalising.

    _init_table = """create table %s (
        subject varchar, predicate varchar, object varchar,
        subject_type char, object_type char,
        context varchar,
        primary key(subject, subject_type, predicate, object, object_type, context)
        )"""
    _init_sequence = "create sequence %s"
    _query_next_bnode_id = "select nextval('%s')"
    _delete_table = "drop table %s"
    _delete_sequence = "drop sequence %s"

    null_context = "None"

    # Methods.

    def __init__(self, connection, context=None, table_name=None, sequence_name=None, debug=0):

        """
        Initialise access to the store via the given 'connection' and employing
        the given, optional 'context' URI, using a table with the given,
        optional 'table_name' ("triples" by default) and a sequence (for BNode
        generation) with the optional 'sequence_name' ("bnode" by default).

        If the optional 'debug' parameter is set to a true value, the SQL
        statements issued to the database system will be displayed on standard
        output.
        """

        self.connection = connection
        self.context = context
        self.table_name = table_name or "triples"
        self.sequence_name = sequence_name or "bnode"
        self.debug = debug

        # Work out what the database system's paramstyle is.

        module = sys.modules.get(connection.__module__)
        self.paramstyle = module.paramstyle

    def get_context(self, context):

        """
        Return a copy of this store which uses the given 'context' to constrain
        operations on the stored triples.
        """

        return self.__class__(self.connection, unicode(context), self.table_name, self.sequence_name, self.debug)

    def contexts(self):

        "Return a list of contexts found in this store."

        try:
            cursor = self.connection.cursor()
            cursor.execute("select distinct context from %s" % self.table_name)
            results = cursor.fetchall()
        finally:
            cursor.close()

        return [row[0] for row in results if row[0] != self.null_context]

    # Value conversion and query preparation methods.

    def _pmark(self, i):

        """
        Return the appropriate parameter marker for the chosen database system.
        """

        if self.paramstyle == "qmark":
            return "?"
        elif self.paramstyle == "numeric":
            return ":%d" % i
        elif self.paramstyle == "named":
            return ":n%d" % i
        elif self.paramstyle == "format":
            return "%s"
        elif self.paramstyle == "pyformat":
            return "%%(n%d)s" % i
        else:
            return "?" # NOTE: Guess a paramstyle.

    def _pmarks(self, s):

        """
        Encode the given string 's' so that parameter markers are suitable for
        the chosen database system.
        """

        parts = s.split("?")
        new_parts = [parts[0]]
        i = 0
        for part in parts[1:]:
            new_parts.append(self._pmark(i))
            new_parts.append(part)
            i = i + 1
        return "".join(new_parts)

    def _present(self, values):

        """
        Present the given 'values' collection in the appropriate form for the
        chosen database system (either as a dictionary mapping parameter names
        to values, or as the provided collection of values).
        """

        if self.paramdict.get(self.paramstyle, 0):
            d = {}
            i = 0
            for value in values:
                d["n%d" % i] = value
                i = i + 1
            return d
        else:
            return values

    def _convert(self, value):

        """
        Convert a 'value' into a Unicode object and a type code.
        """

        type_code = self.names_to_codes.get(value.__class__.__name__, "L")
        if type_code == "B":
            if hasattr(value, "value") and value.value is None:
                value.value = self._get_bnode_id()
            return unicode(value), type_code
        else:
            return unicode(value), type_code

    def _instantiate(self, value, type_code):

        """
        Instantiate and return an object from the given 'value' and 'type_code'.
        """

        return globals()[self.codes_to_names.get(type_code, "Literal")](value)

    def _get_bnode_id(self):

        "Return a BNode identifier using the database."

        cursor = self.connection.cursor()
        try:
            cursor.execute(self._query_next_bnode_id % self.sequence_name)
            results = cursor.fetchone()
        finally:
            cursor.close()
        return "_bnode" + str(results[0])

    def _column(self, name, index=None):

        """
        Return the qualified column name for the given 'name' and optional
        'index'. If 'index' is not specified (or None), an unqualified name
        will be returned.
        """

        if index is None:
            return name
        else:
            return "%s.%s" % (self._table(index), name)

    def _table(self, index=None):

        """
        Return the aliased table name for the given, optional 'index'. If
        'index' is not specified (or None), a plain table name will be returned.
        """

        if index is None:
            return self.table_name
        else:
            return "%s_%s" % (self.table_name, index)

    def _get_conditions(self, pattern, index=None):

        """
        Return a query conditions list and a values list for the given
        'pattern'. If the optional 'index' flag is specified (and set to a value
        other than None), the column names will be qualified with an appropriate
        table name.
        """

        subject, predicate, object = pattern
        conditions = []
        values = []

        # Subjects are always tested for equality.

        if subject is not None:
            subject_value, subject_type = self._convert(subject)
            conditions.append("%s = ?" % self._column("subject", index))
            values.append(subject_value)
            conditions.append("%s = ?" % self._column("subject_type", index))
            values.append(subject_type)

        # Predicates are always tested for equality.

        if predicate is not None:
            conditions.append("%s = ?" % self._column("predicate", index))
            values.append(unicode(predicate))

        # Objects can either be single values tested for equality, Results
        # objects describing some set of already selected results, or more
        # complicated expressions with accompanying literal values.

        if object is not None:

            # Process an expression and values.

            if isinstance(object, tuple):
                comparison, comparison_values = object
                conditions.append(comparison.replace("_", self._column("object", index)))
                values += map(unicode, comparison_values)
                conditions.append("%s = ?" % self._column("object_type", index))
                values.append("L")

            # Process a Results object.

            elif isinstance(object, Results):
                subquery, subquery_values = object.get_child_query()
                conditions.append(subquery)
                values += subquery_values

            # Process a single value.

            else:
                object_value, object_type = self._convert(object)
                conditions.append("%s = ?" % self._column("object", index))
                values.append(object_value)
                conditions.append("%s = ?" % self._column("object_type", index))
                values.append(object_type)

        # Add context-related constraints.

        if self.context:
            conditions.append("%s = ?" % self._column("context", index))
            values.append(self.context)

        return conditions, values

    # Administration methods.
    # NOTE: String interpolation employed in the following initialisation
    # NOTE: methods: do not let user input dictate the supplied names!

    def init(self):

        "Initialise the database by creating a table and a sequence."

        self.init_table()
        self.init_sequence()

    def init_table(self):

        "Initialise the triple store's table."

        cursor = self.connection.cursor()
        cursor.execute(self._init_table % self.table_name)
        cursor.close()

    def init_sequence(self):

        "Initialise the BNode sequence."

        cursor = self.connection.cursor()
        cursor.execute(self._init_sequence % self.sequence_name)
        cursor.close()

    def delete(self):

        "Drop the store's table and sequence."

        self.delete_table()
        self.delete_sequence()

    def delete_table(self):

        "Drop the triple store's table."

        cursor = self.connection.cursor()
        cursor.execute(self._delete_table % self.table_name)
        cursor.close()

    def delete_sequence(self):

        "Drop the BNode sequence."

        cursor = self.connection.cursor()
        cursor.execute(self._delete_sequence % self.sequence_name)
        cursor.close()

    # Connection management methods.

    def close(self):

        "Close the connection to the database system."

        self.connection.close()

    def commit(self):

        "Commit the changes made to the triple store."

        self.connection.commit()

    def rollback(self):

        "Roll back (undo) the changes made to the triple store."

        self.connection.rollback()

    # Non-rdflib querying methods.

    def subject(self, subject):

        "Return a Subject for the given 'subject' identifier."

        return Subject(self, subject)

    def count(self, pattern):

        "Return a count of the triples conforming to the given 'pattern'."

        return CountableResults(self, pattern)

    # Querying and updating methods compatible with rdflib.

    def subjects(self, predicate=None, object=None, ordering=None, limit=None):

        "Return subjects for the given 'predicate' and/or 'object' identifiers."

        return Subjects(self, (None, predicate, object), ordering, limit)

    def predicates(self, subject=None, object=None, ordering=None, limit=None):

        "Return predicates for the given 'subject' and/or 'object' identifiers."

        return Predicates(self, (subject, None, object), ordering, limit)

    def objects(self, subject=None, predicate=None, ordering=None, limit=None):

        "Return objects for the given 'subject' and/or 'predicate' identifiers."

        return Objects(self, (subject, predicate, None), ordering, limit)

    def triples(self, pattern, ordering=None, limit=None):

        "Return triples conforming to the given 'pattern'."

        return Triples(self, pattern, ordering, limit)

    def add(self, pattern):

        "Add a triple using the information found in the given 'pattern'."

        # Find how many triples exist with the given pattern.

        countable = CountableResults(self, pattern)
        if len(countable) != 0:
            return

        # If appropriate, add a new triple.

        cursor = self.connection.cursor()
        try:
            # Where no row existed, insert a new row...

            statement = "insert into %s (subject, predicate, object, subject_type, object_type, context) values (" \
                "?, ?, ?, ?, ?, ?)" % self.table_name
            subject, predicate, object = pattern
            subject_value, subject_type = self._convert(subject)
            object_value, object_type = self._convert(object)
            values = [subject_value, unicode(predicate), object_value, subject_type, object_type, self.context or self.null_context]
            if self.debug:
                print self._pmarks(statement), self._present(values)
            cursor.execute(self._pmarks(statement), self._present(values))
        finally:
            cursor.close()

    def remove(self, pattern):

        "Remove all triples conforming to the given 'pattern'."

        cursor = self.connection.cursor()
        try:
            statement = "delete from %s" % self.table_name
            conditions, values = self._get_conditions(pattern)
            if conditions:
                statement += (" where %s" % " and ".join(conditions))
            if self.debug:
                print statement, self._present(values)
            if values:
                cursor.execute(self._pmarks(statement), self._present(values))
            else:
                cursor.execute(self._pmarks(statement))
        finally:
            cursor.close()

    def remove_context(self, context):

        """
        Removes the specified 'context' from the database.
        """

        s = self.get_context(context)
        s.remove((None, None, None))

# Convenience classes.

class Subject:

    "A class representing a more conveniently accessible subject."

    def __init__(self, store, subject):

        """
        Initialise the subject instance with the given 'store' and 'subject'
        identifier.
        """

        self.store = store
        self.subject = subject

    def __getitem__(self, predicate):
        return self.store.objects(self.subject, predicate)

    def __delitem__(self, predicate):
        if isinstance(predicate, tuple):
            predicate, object = predicate
            self.store.remove((self.subject, predicate, object))
        else:
            self.store.remove((self.subject, predicate, None))

    def __setitem__(self, predicate, object):
        self.store.add((self.subject, predicate, object))

    def keys(self):
        return self.store.predicates(self.subject)

    def values(self):
        return self.store.triples((self.subject, None, None))

    # Results-compatible methods.

    def get_query(self):
        # Always alias the table to permit ordering joins.
        tn = self.store.table_name
        query = "select %s, %s, %s from %s as %s where %s = ? and %s = ? and %s = ?" % (
            self.store._column("subject", 0),
            self.store._column("subject_type", 0),
            self.store._column("context", 0),
            self.store._table(), self.store._table(0),
            self.store._column("subject", 0),
            self.store._column("subject_type", 0),
            self.store._column("context", 0)
            )
        values = list(self.store._convert(self.subject)) + [self.store.context]
        return query, values

    def get_subquery(self):
        # Always alias the table to permit ordering joins.
        tn = self.store.table_name
        internal_query, values = self.get_query()
        query = "(%s, %s, %s) in (%s)" % (
            self.store._column("subject", 0),
            self.store._column("subject_type", 0),
            self.store._column("context", 0),
            internal_query
            )
        return query, values

# Querying classes.

class Results:

    "A class representing a selection of results."

    def __init__(self, store, pattern, ordering=None, limit=None):

        """
        Initialise the results object with the given 'store', 'pattern',
        optional 'ordering' description and optional 'limit' criteria.
        """

        self.store = store
        self.pattern = pattern
        self.results = None
        ordering = ordering or [None]
        self.order_fields = ordering[:-1]
        self.order_direction = ordering[-1]
        self.limit = limit

    def _ensure(self):
        if self.results is None:
            self.results = self._execute()

    def __getitem__(self, i):
        self._ensure()
        return self.results[i]

    def __len__(self):
        self._ensure()
        return len(self.results)

    def __repr__(self):
        self._ensure()
        return repr(self.results)

    def _get_query(self, select_clause):

        """
        Build the query conditions and return a usable query which starts with
        the supplied 'select_clause'.
        """

        # Add joins to support ordering:
        # select ... from T0 inner join T1 on ... inner join T2 on ...

        if self.order_fields:
            for i in range(0, len(self.order_fields) - 1):
                this_table = self.store._table(i)
                next_table = self.store._table(i + 1)
                select_clause += " inner join %s as %s on %s = %s and %s = %s" % (
                    self.store._table(), next_table,
                    self.store._column("object", i), self.store._column("subject", i + 1),
                    self.store._column("object_type", i), self.store._column("subject_type", i + 1)
                    )

        # Add general conditions.

        if isinstance(self.pattern, tuple):
            conditions, values = self.store._get_conditions(self.pattern, index=0)
        else:
            conditions = []
            values = []
            for t in self.pattern:
                subquery, subquery_values = t.get_subquery()
                conditions.append(subquery)
                values += subquery_values

        # Add more conditions related to ordering:
        # where T0.predicate = ... and T1.predicate = ... and T2.predicate = ...

        if self.order_fields:
            i = 0
            for field in self.order_fields:
                if field is not None:
                    conditions.append("%s = ?" % self.store._column("predicate", i))
                    values.append(unicode(field))
                i += 1

        # Add all conditions to the query.

        if conditions:
            query = (select_clause + (" where %s" % " and ".join(conditions)))
        else:
            query = select_clause

        # Add the order clause.

        if self.order_direction:
            query += (" order by %s %s" % (
                self._get_order_column(),
                self.order_direction or "asc"
                ))

        # Add the limit clause.

        if self.limit:
            query += (" limit %s" % self.limit)

        return query, values

    def _get_order_column(self):
        return self.store._column("object", max(0, len(self.order_fields) - 1))

    def get_child_query(self):
        query = "select %s, %s, %s from %s as %s" % (
            self.store._column("subject", 0),
            self.store._column("subject_type", 0),
            self.store._column("context", 0),
            self.store._table(), self.store._table(0)
            )
        query, values = self._get_query(query)
        return "(%s, %s, %s) in (%s)" % (
            self.store._column("object", 0),
            self.store._column("object_type", 0),
            self.store._column("context", 0),
            query
            ), values

class SingleResults(Results):

    "A class representing a selection of single value results."

    def _execute(self):
        cursor = self.store.connection.cursor()
        try:
            query, values = self.get_query()
            if self.store.debug:
                print self.store._pmarks(query), self.store._present(values)
            cursor.execute(self.store._pmarks(query), self.store._present(values))
            # Convert the fetched value using value and type information.
            results = [self.store._instantiate(row[0], row[1]) for row in cursor.fetchall()]
        finally:
            cursor.close()
        return results

class CountableResults(Results):

    "A class representing a count of some results."

    def _execute(self):
        cursor = self.store.connection.cursor()
        try:
            query, values = self.get_query()
            if self.store.debug:
                print self.store._pmarks(query), self.store._present(values)
            cursor.execute(self.store._pmarks(query), self.store._present(values))
            results = cursor.fetchall()
        finally:
            cursor.close()
        return results

    def get_value(self):
        self._ensure()
        return self.results[0][0]

    def __getitem__(self, i):
        raise NotSupportedError, "__getitem__ for CountableResults is not supported"

    def __len__(self):
        # NOTE: Apparent Python limitation on the return value: must use int!
        return int(self.get_value())

    def __repr__(self):
        return str(self.get_value())

    def get_query(self):
        query = "select count(*) from %s as %s" % (self.store._table(), self.store._table(0))
        return self._get_query(query)

    def get_subquery(self):
        raise NotSupportedError, "get_subquery for CountableResults is not supported"

class Subjects(SingleResults):

    "A class representing a selection of subjects."

    def get_query(self):
        query = "select distinct %s, %s, %s" % (
            self.store._column("subject", 0),
            self.store._column("subject_type", 0),
            self.store._column("context", 0)
            )

        if self.order_direction:
            query += ", %s" % self._get_order_column()

        query += " from %s as %s" % (
            self.store._table(), self.store._table(0)
            )
        return self._get_query(query)

    def get_subquery(self):
        internal_query, values = self.get_query()
        query = "(%s, %s, %s) in (%s)" % (
            self.store._column("subject", 0),
            self.store._column("subject_type", 0),
            self.store._column("context", 0),
            internal_query
            )
        return query, values

class Predicates(SingleResults):

    "A class representing a selection of predicates."

    def get_query(self):
        query = "select distinct %s, 'U', %s" % (
            self.store._column("predicate", 0),
            self.store._column("context", 0)
            )

        if self.order_direction:
            query += ", %s" % self._get_order_column()

        query += " from %s as %s" % (
            self.store._table(), self.store._table(0)
            )
        return self._get_query(query)

    def get_subquery(self):
        internal_query, values = self.get_query()
        query = "(%s, 'U', %s) in (%s)" % (
            self.store._column("predicate", 0),
            self.store._column("context", 0),
            internal_query
            )
        return query, values

class Objects(SingleResults):

    "A class representing a selection of objects."

    def get_query(self):
        query = "select distinct %s, %s, %s" % (
            self.store._column("object", 0),
            self.store._column("object_type", 0),
            self.store._column("context", 0)
            )

        if self.order_direction:
            query += ", %s" % self._get_order_column()

        query += " from %s as %s" % (
            self.store._table(), self.store._table(0)
            )
        return self._get_query(query)

    def get_subquery(self):
        internal_query, values = self.get_query()
        query = "(%s, %s, %s) in (%s)" % (
            self.store._column("object", 0),
            self.store._column("object_type", 0),
            self.store._column("context", 0),
            internal_query
            )
        return query, values

class Triples(Results):

    "A class representing a selection of triples."

    def _execute(self):
        cursor = self.store.connection.cursor()
        try:
            query, values = self.get_query()
            if self.store.debug:
                print self.store._pmarks(query), self.store._present(values)
            if values:
                cursor.execute(self.store._pmarks(query), self.store._present(values))
            else:
                cursor.execute(self.store._pmarks(query))
            results = cursor.fetchall()
        finally:
            cursor.close()
        return [(self.store._instantiate(s, st), URIRef(p), self.store._instantiate(o, ot)) for (s, p, o, st, ot, c) in results]

    def get_query(self):
        query = "select %s, %s, %s, %s, %s, %s from %s as %s" % (
            self.store._column("subject", 0),
            self.store._column("predicate", 0),
            self.store._column("object", 0),
            self.store._column("subject_type", 0),
            self.store._column("object_type", 0),
            self.store._column("context", 0),
            self.store._table(), self.store._table(0)
            )
        return self._get_query(query)

    def get_subquery(self):
        internal_query, values = self.get_query()
        query = "(%s, %s, %s, %s, %s, %s) in (%s)" % (
            self.store._column("subject", 0),
            self.store._column("predicate", 0),
            self.store._column("object", 0),
            self.store._column("subject_type", 0),
            self.store._column("object_type", 0),
            self.store._column("context", 0),
            internal_query
            )
        return query, values

# Convenience functions.

def open(database_name=None, connection=None, table_name=None, sequence_name=None, debug=0, **kw):

    """
    Open a triple store using either a connection identified by 'database_name'
    and other keyword arguments or the given 'connection'. If the optional
    'table_name' and 'sequence_name' are provided, override the default settings
    in the TripleStore class in order to access stored information in the
    database. The optional 'debug' parameter (set to false by default) can be
    used to show the working of the triple store.
    """

    if connection is not None:
        c = connection
    else:
        if database_name is not None:
            c = PgSQL.connect(database=database_name, client_encoding="utf-8", unicode_results=1)
        else:
            c = PgSQL.connect(client_encoding="utf-8", unicode_results=1, **kw)
        c.cursor().execute("set client_encoding to unicode")

    return TripleStore(c, table_name, sequence_name, debug=debug)

# Test program.

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print "Specify:"
        print "--database <database-name> to choose a database other than 'testdb'."
        print "--names <table-name> <sequence-name> to choose objects other than 'triples' and 'bnode' respectively."
        print "--init to initialise the database (and to commit the new objects)."
        print "--delete to remove objects from the database (and to commit their removal)."
        print "--contexts to show the contexts found in the database (and to exit immediately)."
        print "--remove <context-name> to remove the specified context (and to exit immediately)."
        print "--context <context-name> to specify a specific context (as opposed to no context)."
        print "--test to test the module."
        print "--debug to show the module's working."
        print "--commit to commit stored data afterwards."
        print "--close to close the connection afterwards."
        print

    # Open the connection.

    if "--database" in sys.argv:
        i = sys.argv.index("--database")
        database_name = sys.argv[i+1]
    else:
        database_name = "testdb"

    # Open the store.

    if "--names" in sys.argv:
        i = sys.argv.index("--names")
        s = open(database_name, table_name=sys.argv[i+1], sequence_name=sys.argv[i+2], debug=("--debug" in sys.argv))
    else:
        s = open(database_name, debug=("--debug" in sys.argv))

    # Initialise the database, if appropriate.

    if "--init" in sys.argv:
        s.init()
        s.commit()

    # Restore the database, if appropriate.

    if "--delete" in sys.argv:
        s.delete()
        s.commit()

    # Show the contexts, if requested.

    if "--contexts" in sys.argv:
        print s.contexts()
        sys.exit(0)

    # Remove the context, if specified.

    if "--remove" in sys.argv:
        i = sys.argv.index("--remove")
        s.remove_context(sys.argv[i+1])
        s.commit()
        print "Context", sys.argv[i+1], "removed."
        sys.exit(0)

    # Get the context, if specified.

    if "--context" in sys.argv:
        i = sys.argv.index("--context")
        s = s.get_context(sys.argv[i+1])

    # Test the store.

    if "--test" in sys.argv:
        s.add((u"a", u"b", u"æøå"))
        s.add((u"a", u"b", Literal(u"æøå"))) # should have no effect
        s.add(("a", "b", "x"))
        result = s.triples(("a", "b", None))
        print "Should be 2 triples:", len(result) == 2
        print result
        print
        s.remove(("a", "b", None))
        result = s.triples(("a", "b", None))
        print "Should be 0 triples:", len(result) == 0
        print result
        print
        s.add(("p", "q", Literal("20050101")))
        s.add(("p", "q", Literal("20050401")))
        s.add(("p", "q", Literal("20051001")))
        s.add(("p", "q", Literal("20060101")))
        result = s.triples(("p", "q", None))
        print "Should be 4 triples:", len(result) == 4
        print result
        print
        result = s.triples(("p", "q", None), ordering=["desc"])
        print "Should be 4 triples (in descending order):", len(result) == 4
        print result
        print
        result = s.triples(("p", "q", ("_ > ? and _ < ?", ["20050301", "20051101"])))
        print "Should be 2 triples:", len(result) == 2
        print result
        print
        result = s.triples(("p", "q", ("_ > ? and _ < ?", ["20050301", "20051101"])), ordering=["q", "asc"])
        print "Should be 2 triples (in order):", len(result) == 2
        print result
        print
        subject = s.subject("p")
        result = subject["q"]
        print "Should be 4 results:", len(result) == 4
        print result
        print
        subject["q"] = "20060301"
        del subject[("q", "20051001")]
        result = subject["q"]
        print "Should be 4 results:", len(result) == 4
        print result
        print
        del subject["q"]
        result = subject["q"]
        print "Should be 0 results:", len(result) == 0
        print result
        print
        s.add((URIRef("xyz"), URIRef("abc"), BNode()))
        result = s.triples((URIRef("xyz"), None, None))
        print "Should be 1 triple:", len(result) == 1
        print result
        print
        s.add((URIRef("a"), URIRef("b"), Literal("1")))
        s.add((URIRef("a"), URIRef("b"), Literal("2")))
        s.add((URIRef("a"), URIRef("b"), Literal("3")))
        s.add((URIRef("a"), URIRef("x"), Literal("1")))
        s.add((URIRef("a"), URIRef("x"), Literal("2")))
        s.add((URIRef("a"), URIRef("x"), Literal("3")))
        s.add((URIRef("b"), URIRef("x"), Literal("3")))
        s.add((URIRef("b"), URIRef("x"), Literal("4")))
        s.add((URIRef("b"), URIRef("x"), Literal("5")))
        t1 = s.triples((None, None, ("_ > ?", Literal("3"))))
        t2 = s.triples((None, URIRef("x"), None))
        result = s.triples([t1, t2])
        print "Should be 2 triples:", len(result) == 2
        print result
        print
        p1 = s.predicates(URIRef("a"))
        result = s.triples([p1, t1, t2])
        print "Should be 2 triples:", len(result) == 2
        print result
        print
        print "Should be 2 predicates:", len(p1) == 2
        print p1
        print
        print "Should be 2 triples:", len(t1) == 2
        print t1
        print
        print "Should be 6 triples:", len(t2) == 6
        print t2
        print
        s1 = s.subjects(URIRef("b"))
        print "Should be 1 result:", len(s1) == 1
        print s1
        print
        s2 = s.subjects(None, ("_ > ?", [Literal("2")]))
        print "Should be 2 results:", len(s2) == 2
        print s2
        print
        s1_and_s2 = s.triples([s1, s2])
        print "Should be 6 triples:", len(s1_and_s2) == 6
        print s1_and_s2
        print
        s1_and_s2 = s.triples([s1, s2], ordering=["asc"])
        print "Should be 6 triples (in order):", len(s1_and_s2) == 6
        print s1_and_s2
        print
        s1_and_s2_x = s.triples([s1, s2], ordering=[URIRef("x"), "asc"])
        print "Should be 3 triples (in order):", len(s1_and_s2_x) == 3
        print s1_and_s2_x
        print
        s.add((URIRef("c"), URIRef("p"), URIRef("a")))
        s.add((URIRef("c"), URIRef("q"), URIRef("a")))
        s.add((URIRef("d"), URIRef("p"), URIRef("a")))
        s.add((URIRef("d"), URIRef("p"), URIRef("b")))
        ordered = s.triples((None, None, None), ordering=[URIRef("p"), URIRef("x"), "asc"])
        print "Should be 9 triples (in order):", len(ordered) == 9
        print ordered
        print
        s1_and_s2_p_x = s.triples((None, URIRef("p"), s1_and_s2), ordering=[URIRef("p"), URIRef("x"), "asc"])
        print "Should be 6 triples (in order):", len(s1_and_s2_p_x) == 6
        print s1_and_s2_p_x
        print
        s.remove((URIRef("c"), URIRef("p"), URIRef("a")))
        s.remove((URIRef("c"), URIRef("q"), URIRef("a")))
        s.remove((URIRef("d"), URIRef("p"), URIRef("a")))
        s.remove((URIRef("d"), URIRef("p"), URIRef("b")))
        subject_a = s.subject(URIRef("a"))
        result = s.triples([t2, subject_a])
        print "Should be 3 triples:", len(result) == 3
        print result
        print
        t1_and_t2 = s.count([t1, t2])
        print "Should be 2:", len(t1_and_t2) == 2
        print len(t1_and_t2)
        print
        s.add((URIRef("c"), URIRef("y"), URIRef("a")))
        result = s.triples((None, None, t2))
        print "Should be 1 triple:", len(result) == 1
        print result
        print
        result = s.triples((None, None, s2))
        print "Should be 1 triple:", len(result) == 1
        print result
        print

    # Commit data if requested.

    if "--commit" in sys.argv:
        s.commit()

    # Close the store (and the connection) if requested.

    if "--close" in sys.argv:
        s.close()

# vim: tabstop=4 expandtab shiftwidth=4
