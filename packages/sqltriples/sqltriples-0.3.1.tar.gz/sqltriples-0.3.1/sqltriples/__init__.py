#!/usr/bin/env python

"""
A simple SQL-accessible RDF triple store.

Copyright (C) 2006, 2007 Paul Boddie <paul@boddie.org.uk>

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

__version__ = "0.3.1"

from sqltriples.Store import TripleStore, NotSupportedError
from sqltriples.Adapters import PgSQLAdapter, pysqlite2Adapter

# For convenience...

from sqltriples.Types import *

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
            raise NotSupportedError, database_module_name

    else:
        raise NotSupportedError, "Only specified connections or named databases may be opened."

    return TripleStore(a, table_name, sequence_name, debug=debug)

# vim: tabstop=4 expandtab shiftwidth=4
