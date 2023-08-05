#!/usr/bin/env python

"""
RDF triple store classes.

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
"""

from sqltriples.Types import *
from sqltriples.Query import *

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

    # Convenience attributes.

    Literal = Literal
    Namespace = Namespace
    URIRef = URIRef
    BNode = BNode
    TYPE = TYPE

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

        # Useful classes.

        self.Expression = Expression
        self.Pattern = Pattern
        self.Defined = Defined

        # Useful values.

        self.ALL = ALL

        # Special flags.

        self.supports_querying = 1

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

    def _get_condition(self, value, column_name, conditions, values, index, new_index):

        """
        For the given 'value' and using the given 'column_name', add a condition
        to the given 'conditions' list and any associated values to the given
        'values' list. The specified 'index' is used to qualify table
        references.

        The specified 'value' can either be a single value tested for equality,
        a query describing some set of already selected results, more
        complicated expressions with accompanying literal values, or a list of
        single values comprising a set of possible matching values for the
        resulting query.

        Return the new table index, based on the given value of 'index'.
        """

        if isinstance(value, self.Defined):
            conditions.append("%s is not null" % self._column(column_name, index))

        # Process an expression.

        elif isinstance(value, Expression) or isinstance(value, tuple):

            # Add the expression as a condition in the generated query.

            comparison, comparison_values = value
            conditions.append(comparison.replace("_", self._column(column_name, index)))
            values += map(unicode, comparison_values)

            if column_name != "predicate":
                conditions.append("%s = ?" % self._column(column_name + "_type", index))

                # NOTE: Improve this mechanism.

                if hasattr(value, "value_type"):
                    values.append(value.value_type)
                else:
                    values.append("L")

        # Process a query.

        elif isinstance(value, AbstractQuery):

            # Connect the query to this pattern, specifying a role it has by
            # providing column names which connect to columns in the query.

            if column_name != "predicate":
                subquery, subquery_values, new_index = value.get_subquery(
                    [(column_name, column_name + "_type", 0)], index, new_index, match_first=1
                    )
            else:
                subquery, subquery_values, new_index = value.get_subquery(
                    [("predicate", None, 0)], index, new_index, match_parent=1
                    )
            conditions.append(subquery)
            values += subquery_values

        # Process a list of values.

        elif isinstance(value, list):

            # Add the values in the list as a set from which one of the values
            # must match the stated column's value.

            conditions.append("%s in (%s)" % (
                self._column(column_name, index),
                ", ".join(["?"] * len(value))
                ))
            for v in value:
                values.append(unicode(v))

        # Process a single value.

        elif value is not None:

            # Provide a condition which tests the stated column against the
            # specified value.

            value_value, value_type = self._convert(value)
            conditions.append("%s = ?" % self._column(column_name, index))
            values.append(value_value)

            if column_name != "predicate":
                conditions.append("%s = ?" % self._column(column_name + "_type", index))
                values.append(value_type)

        return new_index

    def _get_conditions(self, pattern, index=None, new_index=None):

        """
        Return a query conditions list and a values list for the given
        'pattern'. If the optional 'index' flag is specified (and set to a value
        other than None), the column names will be qualified with an appropriate
        table name.
        """

        subject, predicates, object = pattern[0], pattern[1:-1], pattern[-1]
        conditions = []
        values = []

        # The current table index which may be changed by nested queries.

        new_index = new_index or index

        # Handle deletion-based conditions as well as selection-based ones.
        # (This is done automatically here because index == None can be handled
        # correctly by _get_condition.)

        new_index = self._get_condition(subject, "subject", conditions, values, index, new_index)

        i = 0
        for predicate in predicates:

            # Handle deletion-based conditions as well as selection-based ones.

            if index is None:
                new_index = self._get_condition(predicate, "predicate", conditions, values, None, new_index)
            else:
                new_index = self._get_condition(predicate, "predicate", conditions, values, index + i, new_index)
            i += 1

        # Handle deletion-based conditions as well as selection-based ones.

        if index is None:
            new_index = self._get_condition(object, "object", conditions, values, None, new_index)
        else:
            i = max(0, i - 1)
            new_index = self._get_condition(object, "object", conditions, values, index + i, new_index)

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
        self.init_index()
        self.init_sequence()

    def init_table(self):

        "Initialise the triple store's table."

        cursor = self.connection.cursor()
        try:
            self.adapter.init_table(cursor, self.table_name)
        finally:
            cursor.close()

    def init_sequence(self):

        "Initialise the BNode sequence."

        cursor = self.connection.cursor()
        try:
            self.adapter.init_sequence(cursor, self.sequence_name)
        finally:
            cursor.close()

    def init_index(self):

        "Initialise an index for certain columns."

        cursor = self.connection.cursor()
        try:
            self.adapter.init_index(cursor, self.table_name)
        finally:
            cursor.close()

    def delete(self):

        "Drop the store's table and sequence."

        self.delete_index()
        self.delete_table()
        self.delete_sequence()

    def delete_table(self):

        "Drop the triple store's table."

        cursor = self.connection.cursor()
        try:
            self.adapter.delete_table(cursor, self.table_name)
        finally:
            cursor.close()

    def delete_sequence(self):

        "Drop the BNode sequence."

        cursor = self.connection.cursor()
        try:
            self.adapter.delete_sequence(cursor, self.sequence_name)
        finally:
            cursor.close()

    def delete_index(self):

        "Drop the index from certain columns."

        cursor = self.connection.cursor()
        try:
            self.adapter.delete_index(cursor, self.table_name)
        finally:
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

    def count(self, pattern=None, expression=None):

        "Return a count of the triples conforming to the given 'pattern'."

        return CountableResults(self, pattern or ALL, expression=expression)

    # Querying and updating methods compatible with rdflib.

    def subjects(self, predicate=None, object=None, pattern=None, expression=None, ordering=None, order_by=None, limit=None):

        """
        Return subjects for the given 'predicate' and/or 'object' identifiers.

        Where the 'ordering' is specified (as either "asc" or "desc"), a query
        is produced which sorts the results according to retrieved objects.

        Where the 'order_by' qualifier can be used to choose whether the
        "subject" or the "object" will order the results.

        Where a 'limit' is specified (as an integer), the number of results will
        be limited to the stated amount.
        """

        if pattern is not None:
            return Subjects(self, pattern, expression=expression, ordering=ordering, order_by=order_by, limit=limit)
        else:
            return Subjects(self, (None, predicate, object), expression=expression, ordering=ordering, order_by=order_by, limit=limit)

    def predicates(self, subject=None, object=None, pattern=None, expression=None, ordering=None, order_by=None, limit=None):

        """
        Return predicates for the given 'subject' and/or 'object' identifiers.

        Where the 'ordering' is specified (as either "asc" or "desc"), a query
        is produced which sorts the results according to retrieved objects.

        Where the 'order_by' qualifier can be used to choose whether the
        "subject" or the "object" will order the results.

        Where a 'limit' is specified (as an integer), the number of results will
        be limited to the stated amount.
        """

        if pattern is not None:
            return Predicates(self, pattern, expression=expression, ordering=ordering, order_by=order_by, limit=limit)
        else:
            return Predicates(self, (subject, None, object), expression=expression, ordering=ordering, order_by=order_by, limit=limit)

    def objects(self, subject=None, predicate=None, pattern=None, expression=None, functions=None, ordering=None, order_by=None, limit=None):

        """
        Return objects for the given 'subject' and/or 'predicate' identifiers.

        Where the given 'functions' dictionary is specified, a function will be
        applied for all columns named as keys in that dictionary. For example,
        the following dictionary...

        {"object", "substr(_, 1, 4)"}

        ...results in the following function being applied in the underlying
        query:

        substr(object, 1, 4)

        Where the 'ordering' is specified (as either "asc" or "desc"), a query
        is produced which sorts the results according to retrieved objects.

        Where the 'order_by' qualifier can be used to choose whether the
        "subject" or the "object" will order the results.

        Where a 'limit' is specified (as an integer), the number of results will
        be limited to the stated amount.
        """

        if pattern is not None:
            return Objects(self, pattern, expression=expression, functions=functions, ordering=ordering, order_by=order_by, limit=limit)
        else:
            return Objects(self, (subject, predicate, None), expression=expression, functions=functions, ordering=ordering, order_by=order_by, limit=limit)

    def triples(self, pattern=None, expression=None, functions=None, ordering=None, order_by=None, limit=None):

        """
        Return triples conforming to the given 'pattern'.

        Where the given 'functions' dictionary is specified, a function will be
        applied for all columns named as keys in that dictionary. For example,
        the following dictionary...

        {"object", "substr(_, 1, 4)"}

        ...results in the following function being applied in the underlying
        query:

        substr(object, 1, 4)

        Where the 'ordering' is specified (as either "asc" or "desc"), a query
        is produced which sorts the results according to retrieved objects.

        Where the 'order_by' qualifier can be used to choose whether the
        "subject" or the "object" will order the results.

        Where a 'limit' is specified (as an integer), the number of results will
        be limited to the stated amount.
        """

        return Triples(self, pattern or ALL, expression=expression, functions=functions, ordering=ordering, order_by=order_by, limit=limit)

    def tuples(self, pattern=None, expression=None, functions=None, ordering=None, order_by=None, limit=None, partial=0):
        return Tuples(self, pattern or ALL, expression=expression, functions=functions, ordering=ordering, order_by=order_by, limit=limit, partial=partial)

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

    # Additional methods.

    def not_subjects(self, result):
        return NegationOfSubjects(self, result)

    def not_predicates(self, result):
        return NegationOfPredicates(self, result)

    def not_objects(self, result):
        return NegationOfObjects(self, result)

    def not_triples(self, result):
        return NegationOfTriples(self, result)

    def not_tuples(self, result, pattern=ALL):
        return NegationOfTuples(self, result, pattern)

    def and_subjects(self, queries):
        return ConjunctionOfSubjects(self, queries)

    def and_predicates(self, queries):
        return ConjunctionOfPredicates(self, queries)

    def and_objects(self, queries):
        return ConjunctionOfObjects(self, queries)

    def and_triples(self, queries):
        return ConjunctionOfTriples(self, queries)

    def and_tuples(self, queries, pattern=ALL):
        return ConjunctionOfTuples(self, queries, pattern)

    def or_subjects(self, queries):
        return DisjunctionOfSubjects(self, queries)

    def or_predicates(self, queries):
        return DisjunctionOfPredicates(self, queries)

    def or_objects(self, queries):
        return DisjunctionOfObjects(self, queries)

    def or_triples(self, queries):
        return DisjunctionOfTriples(self, queries)

    def or_tuples(self, queries, pattern=ALL):
        return DisjunctionOfTuples(self, queries, pattern)

    def intersect_subjects(self, queries):
        return IntersectionOfSubjects(self, queries)

    def intersect_predicates(self, queries):
        return IntersectionOfPredicates(self, queries)

    def intersect_objects(self, queries):
        return IntersectionOfObjects(self, queries)

    def intersect_triples(self, queries):
        return IntersectionOfTriples(self, queries)

    def intersect_tuples(self, queries, pattern=ALL):
        return IntersectionOfTuples(self, queries, pattern)

    # Enhanced store methods.

    def has_triple(self, pattern):
        for t in self.triples(pattern):
            return 1
        return 0

# vim: tabstop=4 expandtab shiftwidth=4
