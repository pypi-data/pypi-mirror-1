#!/usr/bin/env python

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

To initialise the database, first open a store:

from sqltriples import TripleStore, PgSQLAdapter # using PgSQL
adapter = PgSQLAdapter(connection)
store = TripleStore(adapter) # "triples" is the default table name

Alternatively, use the open function:

import sqltriples
store = sqltriples.open(dbname, dbmodulename)

Then, use the init method on the TripleStore object as follows:

store.init()
store.commit()

See the attributes of the different adapter classes for details of the table and
sequence employed.

To remove the triple store objects from the database, use the delete method on
the TripleStore object as follows:

store.delete()
store.commit()

NOTE: The statements sent to the database system can be configured, but this
NOTE: should be made convenient in future releases.
"""

__version__ = "0.2"

import sys
import time, random # for sqlite support

# Exceptions.

class NotSupportedError(Exception):
    pass

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

# Database-specific classes.

class Adapter:

    # A table indicating whether a paramstyle mandates a dictionary when values
    # are being presented to the database system.

    paramdict = {
        "qmark" : 0, "numeric" : 0, "named" : 1, "format" : 0, "pyformat" : 1
        }

    def __init__(self, connection):
        self.connection = connection

    def _pmark(self, i):
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

    def _present(self, values):
        if self.paramdict.get(self.paramstyle, 0):
            d = {}
            i = 0
            for value in values:
                d["n%d" % i] = value
                i = i + 1
            return d
        else:
            return values

    def init_table(self, cursor, table_name):
        cursor.execute(self._init_table % table_name)

    def init_sequence(self, cursor, sequence_name):
        pass

    def delete_table(self, cursor, table_name):
        cursor.execute(self._delete_table % table_name)

    def delete_sequence(self, cursor, sequence_name):
        pass

    def query_next_bnode_id(self, cursor, sequence_name):
        cursor.execute(self._query_next_bnode_id % sequence_name)
        return str(cursor.fetchone()[0])

class PgSQLAdapter(Adapter):
    paramstyle = "pyformat"

    _init_table = """
        create table %s (
            subject varchar, predicate varchar, object varchar,
            subject_type char, object_type char,
            context varchar,
            primary key(subject, subject_type, predicate, object, object_type, context)
        )
        """
    _init_sequence = "create sequence %s"
    _delete_table = "drop table %s"
    _delete_sequence = "drop sequence %s"
    _query_next_bnode_id = "select nextval('%s')"

    def init_sequence(self, cursor, sequence_name):
        cursor.execute(self._init_sequence % sequence_name)

    def delete_sequence(self, cursor, sequence_name):
        cursor.execute(self._delete_sequence % sequence_name)

class pysqlite2Adapter(Adapter):
    paramstyle = "qmark"

    _init_table = """
        create table %s (
            subject text, predicate text, object text,
            subject_type char, object_type char,
            context text,
            primary key(subject, subject_type, predicate, object, object_type, context)
        )
        """
    _delete_table = "drop table %s"

    def query_next_bnode_id(self, cursor, sequence_name):
        # NOTE: sqlite doesn't support sequences sensibly.
        # NOTE: This could be substantially improved.
        return "%s%s" % (long(time.time() * 10000000), random.randint(0, 1000000000))

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

    # We need a non-null name for "null" contexts.

    null_context = "None"

    # Methods.

    def __init__(self, adapter, context=None, table_name=None, sequence_name=None, debug=0):

        """
        Initialise access to the store via the given 'adapter' and employing
        the given, optional 'context' URI, using a table with the given,
        optional 'table_name' ("triples" by default) and a sequence (for BNode
        generation) with the optional 'sequence_name' ("bnode" by default).

        If the optional 'debug' parameter is set to a true value, the SQL
        statements issued to the database system will be displayed on standard
        output.
        """

        self.adapter = adapter
        self.connection = self.adapter.connection
        self.context = context
        self.table_name = table_name or "triples"
        self.sequence_name = sequence_name or "bnode"
        self.debug = debug

    def get_context(self, context):

        """
        Return a copy of this store which uses the given 'context' to constrain
        operations on the stored triples.
        """

        return self.__class__(self.adapter, unicode(context), self.table_name, self.sequence_name, self.debug)

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

        return self.adapter._pmark(i)

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

        return self.adapter._present(values)

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
            bnode_id = self.adapter.query_next_bnode_id(cursor, self.sequence_name)
        finally:
            cursor.close()
        return "_bnode" + bnode_id

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

        new_index = index # the current table index - may be changed by nested queries

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
                subquery, subquery_values, new_index = object.get_child_query(index)
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

        return conditions, values, new_index

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
        self.adapter.init_table(cursor, self.table_name)
        cursor.close()

    def init_sequence(self):

        "Initialise the BNode sequence."

        cursor = self.connection.cursor()
        self.adapter.init_sequence(cursor, self.sequence_name)
        cursor.close()

    def delete(self):

        "Drop the store's table and sequence."

        self.delete_table()
        self.delete_sequence()

    def delete_table(self):

        "Drop the triple store's table."

        cursor = self.connection.cursor()
        self.adapter.delete_table(cursor, self.table_name)
        cursor.close()

    def delete_sequence(self):

        "Drop the BNode sequence."

        cursor = self.connection.cursor()
        self.adapter.delete_sequence(cursor, self.sequence_name)
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

        return Subjects(self, (None, predicate, object), ordering=ordering, limit=limit)

    def predicates(self, subject=None, object=None, ordering=None, limit=None):

        "Return predicates for the given 'subject' and/or 'object' identifiers."

        return Predicates(self, (subject, None, object), ordering=ordering, limit=limit)

    def objects(self, subject=None, predicate=None, fn=None, ordering=None, limit=None):

        """
        Return objects for the given 'subject' and/or 'predicate' identifiers.
        Where the given function 'fn' is specified (as a string containing a
        reference to selected objects as denoted by the "_" character), this
        function is applied the underlying query; for example:

        "substring(_ from 1 for 4)"

        Where the 'ordering' is specified (as a tuple optionally containing
        predicates and ending with a ordering "direction" - either "asc" or
        "desc"), a query is produced which attempts to find objects through the
        traversal of triples via the predicates and to sort them accordingly;
        for example:

        ("pr1", "pr2", "asc")

        Where a 'limit' is specified (as an integer), the number of results will
        be limited to the stated amount.
        """

        return Objects(self, (subject, predicate, None), fn=fn, ordering=ordering, limit=limit)

    def triples(self, pattern, ordering=None, limit=None):

        "Return triples conforming to the given 'pattern'."

        return Triples(self, pattern, ordering=ordering, limit=limit)

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
            conditions, values, new_index = self._get_conditions(pattern)
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

    def get_query(self, index, constraints=None):

        """
        Produce for 'index' something like this:

        select ... from triples as triples_i0 where ...
        """

        query = "select %s, %s, %s from %s as %s where %s = ? and %s = ? and %s = ?" % (
            self.store._column("subject", index),
            self.store._column("subject_type", index),
            self.store._column("context", index),
            self.store._table(), self.store._table(index),
            self.store._column("subject", index),
            self.store._column("subject_type", index),
            self.store._column("context", index)
            )
        if constraints:
            query += " and " + constraints
        values = list(self.store._convert(self.subject)) + [self.store.context or self.store.null_context]
        return query, values, index

    def get_subquery(self, parent_index, index):

        """
        Produce for 'index' something like this:

        exists (select ... from triples as triples_i1 where ...
                and triples_i0.subject = triples_i1.subject ...)
        """

        constraints = "%s = %s and %s = %s and %s = %s" % (
            self.store._column("subject", parent_index),
            self.store._column("subject", index + 1),
            self.store._column("subject_type", parent_index),
            self.store._column("subject_type", index + 1),
            self.store._column("context", parent_index),
            self.store._column("context", index + 1)
            )
        internal_query, values, new_index = self.get_query(index + 1, constraints)
        query = "exists (%s)" % internal_query
        return query, values, new_index

# Querying classes.

class Results:

    """
    A class representing a selection of results.

    Interaction with objects based on this class is typically done using the
    'get_query' method, and this method makes uses of the '_get_query' mechanism
    described below in order to produce a suitable top-level query that produces
    results of the expected form.

    This class provides a '_get_query' method which produces the core of most
    querying operations, comprising mostly of producing conditions based on each
    object's pattern, ordering and limit information. Where patterns specified
    in the initialisation of objects involve other objects based on this class,
    such objects are requested to provide a subquery via the 'get_subquery'
    method which itself provides a means of combining an outer query with a
    specific subquery (which in turn is produced by '_get_query' for that
    object).
    """

    def __init__(self, store, pattern, fn=None, ordering=None, limit=None):

        """
        Initialise the results object with the given 'store', 'pattern',
        optional 'ordering' description and optional 'limit' criteria.
        """

        self.store = store
        self.pattern = pattern
        self.fn = fn
        ordering = ordering or [None]
        self.order_fields = ordering[:-1]
        self.order_direction = ordering[-1]
        self.limit = limit
        self.results = None

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

    def _get_query(self, select_clause, index, constraints=None):

        """
        Build the query conditions and return a usable query which starts with
        the supplied 'select_clause' and which uses the given table 'index'
        number as qualifier.
        """

        # Add joins to support ordering:
        # select ... from T0 inner join T1 on ... inner join T2 on ...

        if self.order_fields:
            for i in range(0, len(self.order_fields) - 1):
                if i == 0:
                    this_index = index + i
                else:
                    this_index = "order_%s" % (index + i)
                next_index = "order_%s" % (index + i + 1)
                select_clause += " inner join %s as %s on %s = %s and %s = %s" % (
                    self.store._table(), self.store._table(next_index),
                    self.store._column("object", this_index), self.store._column("subject", next_index),
                    self.store._column("object_type", this_index), self.store._column("subject_type", next_index)
                    )

        # Add general conditions.

        if isinstance(self.pattern, tuple):
            conditions, values, new_index = self.store._get_conditions(self.pattern, index=index)
        else:
            conditions = []
            values = []
            new_index = index
            for t in self.pattern:
                subquery, subquery_values, new_index = t.get_subquery(index, new_index)
                conditions.append(subquery)
                values += subquery_values

        # Add more conditions related to ordering:
        # where T0.predicate = ... and T1.predicate = ... and T2.predicate = ...

        if self.order_fields:
            i = 0
            for field in self.order_fields:
                if i == 0:
                    this_index = index + i
                else:
                    this_index = "order_%s" % (index + i)
                if field is not None:
                    conditions.append("%s = ?" % self.store._column("predicate", this_index))
                    values.append(unicode(field))
                i += 1

        # Add the constraints as an additional condition.

        if constraints:
            conditions.append(constraints)

        # Add all conditions to the query.

        if conditions:
            query = (select_clause + (" where %s" % " and ".join(conditions)))
        else:
            query = select_clause

        # Add the order clause.

        if self.order_direction:
            query += (" order by %s %s" % (
                self._get_order_column(index),
                self.order_direction or "asc"
                ))

        # Add the limit clause.

        if self.limit:
            query += (" limit %s" % self.limit)

        return query, values, new_index

    def _get_order_extent(self):
        return max(0, len(self.order_fields) - 1)

    def _get_order_column(self, index):
        i = self._get_order_extent()
        if i == 0:
            this_index = index + i
        else:
            this_index = "order_%s" % (index + i)
        return self.store._column("object", this_index)

    def get_child_query(self, index):

        """
        Obtain the query clause and values (as a 2-tuple) which links this
        object's query to a parent query. Employ the given 'index' to correctly
        qualify the clause's "exposed" columns.
        """

        query = "select * from %s as %s" % (
            self.store._table(), self.store._table(index + 1)
            )
        constraints = "%s = %s and %s = %s and %s = %s" % (
            self.store._column("object", index),
            self.store._column("subject", index + 1),
            self.store._column("object_type", index),
            self.store._column("subject_type", index + 1),
            self.store._column("context", index),
            self.store._column("context", index + 1)
            )
        query, values, new_index = self._get_query(query, index + 1, constraints)
        return "exists (%s)" % query, values, new_index

    def _apply_function(self, fn, column):
        if fn is not None:
            return fn.replace("_", column)
        else:
            return column

class SingleResults(Results):

    "A class representing a selection of single value results."

    def _execute(self):
        cursor = self.store.connection.cursor()
        try:
            query, values, new_index = self.get_query(0)
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
            query, values, new_index = self.get_query(0)
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

    def get_query(self, index):
        query = "select count(*) from %s as %s" % (self.store._table(), self.store._table(index))
        return self._get_query(query, index)

    def get_subquery(self, parent_index, index):
        raise NotSupportedError, "get_subquery for CountableResults is not supported"

class Subjects(SingleResults):

    "A class representing a selection of subjects."

    def get_query(self, index, constraints=None):

        """
        Produce for 'index' something like this:

        select ... from triples as triples_i0 where ...
        """

        query = "select distinct %s, %s, %s" % (
            self.store._column("subject", index),
            self.store._column("subject_type", index),
            self.store._column("context", index)
            )

        if self.order_direction:
            query += ", %s" % self._get_order_column()

        query += " from %s as %s" % (
            self.store._table(), self.store._table(index)
            )
        return self._get_query(query, index, constraints)

    def get_subquery(self, parent_index, index):

        """
        Produce for 'index' something like this:

        exists (select ... from triples as triples_i1 where ...
                and triples_i0.subject = triples_i1.subject ...)
        """

        constraints = "%s = %s and %s = %s and %s = %s" % (
            self.store._column("subject", parent_index),
            self.store._column("subject", index + 1),
            self.store._column("subject_type", parent_index),
            self.store._column("subject_type", index + 1),
            self.store._column("context", parent_index),
            self.store._column("context", index + 1)
            )
        internal_query, values, new_index = self.get_query(index + 1, constraints)
        query = "exists (%s)" % internal_query
        return query, values, new_index

class Predicates(SingleResults):

    "A class representing a selection of predicates."

    def get_query(self, index, constraints=None):

        """
        Produce for 'index' something like this:

        select ... from triples as triples_i0 where ...
        """

        query = "select distinct %s, 'U', %s" % (
            self.store._column("predicate", index),
            self.store._column("context", index)
            )

        if self.order_direction:
            query += ", %s" % self._get_order_column()

        query += " from %s as %s" % (
            self.store._table(), self.store._table(index)
            )
        return self._get_query(query, index, constraints)

    def get_subquery(self, parent_index, index):

        """
        Produce for 'index' something like this:

        exists (select ... from triples as triples_i1 where ...
                and triples_i0.predicate = triples_i1.predicate ...)
        """

        constraints = "%s = %s and %s = %s" % (
            self.store._column("predicate", parent_index),
            self.store._column("predicate", index + 1),
            self.store._column("context", parent_index),
            self.store._column("context", index + 1)
            )
        internal_query, values, new_index = self.get_query(index + 1, constraints)
        query = "exists (%s)" % internal_query
        return query, values, new_index

class Objects(SingleResults):

    "A class representing a selection of objects."

    def get_query(self, index, constraints=None):

        """
        Produce for 'index' something like this:

        select ... from triples as triples_i0 where ...
        """

        query = "select distinct %s, %s, %s" % (
            self._apply_function(self.fn, self.store._column("object", index)),
            self.store._column("object_type", index),
            self.store._column("context", index)
            )

        if self.order_direction:
            query += ", %s" % self._get_order_column()

        query += " from %s as %s" % (
            self.store._table(), self.store._table(index)
            )
        return self._get_query(query, index, constraints)

    def get_subquery(self, parent_index, index):

        """
        Produce for 'index' something like this:

        exists (select ... from triples as triples_i1 where ...
                and triples_i0.object = triples_i1.object ...)
        """

        constraints = "%s = %s and %s = %s and %s = %s" % (
            self.store._column("object", parent_index),
            self.store._column("object", index + 1),
            self.store._column("object_type", parent_index),
            self.store._column("object_type", index + 1),
            self.store._column("context", parent_index),
            self.store._column("context", index + 1)
            )
        internal_query, values, new_index = self.get_query(index + 1, constraints)
        query = "exists (%s)" % internal_query
        return query, values, new_index

class Triples(Results):

    "A class representing a selection of triples."

    def _execute(self):
        cursor = self.store.connection.cursor()
        try:
            query, values, new_index = self.get_query(0)
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

    def get_query(self, index, constraints=None):

        """
        Produce for 'index' something like this:

        select ... from triples as triples_i0 where ...
        """

        query = "select %s, %s, %s, %s, %s, %s from %s as %s" % (
            self.store._column("subject", index),
            self.store._column("predicate", index),
            self.store._column("object", index),
            self.store._column("subject_type", index),
            self.store._column("object_type", index),
            self.store._column("context", index),
            self.store._table(), self.store._table(index)
            )
        return self._get_query(query, index, constraints)

    def get_subquery(self, parent_index, index):

        """
        Produce for 'index' something like this:

        exists (select ... from triples as triples_i1 where ...
                and triples_i0.subject = triples_i1.subject ...)
        """

        constraints = "%s = %s and %s = %s and %s = %s and %s = %s and %s = %s and %s = %s" % (
            self.store._column("subject", parent_index),
            self.store._column("subject", index + 1),
            self.store._column("predicate", parent_index),
            self.store._column("predicate", index + 1),
            self.store._column("object", parent_index),
            self.store._column("object", index + 1),
            self.store._column("subject_type", parent_index),
            self.store._column("subject_type", index + 1),
            self.store._column("object_type", parent_index),
            self.store._column("object_type", index + 1),
            self.store._column("context", parent_index),
            self.store._column("context", index + 1)
            )
        internal_query, values, new_index = self.get_query(index + 1, constraints)
        query = "exists (%s)" % internal_query
        return query, values, new_index

# Convenience functions.

def open(database_name=None, database_module_name=None, adapter=None, table_name=None, sequence_name=None, debug=0, **kw):

    """
    Open a triple store using either a connection identified by 'database_name'
    and using the given 'database_module_name' along with other keyword
    arguments, or using the given 'adapter' object. If the optional 'table_name'
    and 'sequence_name' are provided, override the default settings in the
    TripleStore class in order to access stored information in the database. The
    optional 'debug' parameter (set to false by default) can be used to show the
    working of the triple store.
    """

    if adapter is not None:
        a = adapter

    elif database_module_name is not None:

        if database_module_name == "PgSQL":
            from pyPgSQL import PgSQL
            database_module = PgSQL
            if database_name is not None:
                c = database_module.connect(database=database_name, client_encoding="utf-8", unicode_results=1, **kw)
            else:
                c = database_module.connect(client_encoding="utf-8", unicode_results=1, **kw)
            c.cursor().execute("set client_encoding to unicode")
            a = PgSQLAdapter(c)

        elif database_module_name == "pysqlite2":
            import pysqlite2.dbapi2
            database_module = pysqlite2.dbapi2
            if database_name is not None:
                c = database_module.connect(database=database_name, **kw)
            else:
                c = database_module.connect(**kw)
            a = pysqlite2Adapter(c)

        else:
            raise NotSupportedError, database_module.__name__

    else:
        raise NotSupportedError, "Only specified connections or named databases may be opened."

    return TripleStore(a, table_name, sequence_name, debug=debug)

# vim: tabstop=4 expandtab shiftwidth=4
