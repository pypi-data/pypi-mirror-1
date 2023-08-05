#!/usr/bin/env python

"""
Database-specific adapter classes.

Copyright (C) 2006 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import time, random

class Adapter:
    supports_in_tuples = 0

    # A table indicating whether a paramstyle mandates a dictionary when values
    # are being presented to the database system.

    _paramdict = {
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
        if self._paramdict.get(self.paramstyle, 0):
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

    def init_index(self, cursor, table_name):
        cursor.execute(self._init_index_subject % (table_name, table_name))
        cursor.execute(self._init_index_predicate % (table_name, table_name))
        cursor.execute(self._init_index_object % (table_name, table_name))

    def delete_table(self, cursor, table_name):
        cursor.execute(self._delete_table % table_name)

    def delete_sequence(self, cursor, sequence_name):
        pass

    def delete_index(self, cursor, table_name):
        cursor.execute(self._delete_index_subject % table_name)
        cursor.execute(self._delete_index_predicate % table_name)
        cursor.execute(self._delete_index_object % table_name)

    def query_next_bnode_id(self, cursor, sequence_name):
        cursor.execute(self._query_next_bnode_id % sequence_name)
        return str(cursor.fetchone()[0])

class PgSQLAdapter(Adapter):
    supports_in_tuples = 1
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
    _init_index_subject = "create index %s_subject on %s(subject)"
    _init_index_predicate = "create index %s_predicate on %s(predicate)"
    _init_index_object = "create index %s_object on %s(object)"
    _delete_table = "drop table %s"
    _delete_sequence = "drop sequence %s"
    _delete_index_subject = "drop index %s_subject"
    _delete_index_predicate = "drop index %s_predicate"
    _delete_index_object = "drop index %s_object"
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
    _init_index_subject = "create index %s_subject on %s(subject)"
    _init_index_predicate = "create index %s_predicate on %s(predicate)"
    _init_index_object = "create index %s_object on %s(object)"
    _delete_table = "drop table %s"
    _delete_index_subject = "drop index %s_subject"
    _delete_index_predicate = "drop index %s_predicate"
    _delete_index_object = "drop index %s_object"

    def query_next_bnode_id(self, cursor, sequence_name):
        # NOTE: sqlite doesn't support sequences sensibly.
        # NOTE: This could be substantially improved.
        return "%s%s" % (long(time.time() * 10000000), random.randint(0, 1000000000))

# vim: tabstop=4 expandtab shiftwidth=4
