#!/usr/bin/env python

"Administer an sqltriples database."

import sqltriples
import cmdsyntax
import sys

syntax = cmdsyntax.Syntax("""
    --database=DATABASE_NAME
    --module=MODULE_NAME
    ( --init | --delete | --contexts | --remove-context=CONTEXT_NAME )
    [ --table-name=TABLE_NAME ]
    [ --sequence-name=SEQUENCE_NAME ]
    [ --debug ]
    """)

syntax_matches = syntax.get_args(sys.argv[1:])

try:
    args = syntax_matches[0]
except IndexError:
    print "Use the --database option to indicate which database is being altered."
    print "Use the --module option to indicate which kind of database system is being used."
    print "(Try PgSQL or pysqlite2.)"
    print "Operations:"
    print "The --init option initialises the database."
    print "The --delete option removes all triple store information from a database."
    print "The --contexts option lists all contexts in a database."
    print "The --remove-context option permits the removal of the named context."
    print "Optional arguments:"
    print "Use the --table-name option to specify the table in which triple store information is deposited."
    print "Use the --sequence-name option to specify the sequence from which BNode identifiers are obtained."
    print "(By default, 'triples' is used as the table name; 'bnode' is used as the sequence name.)"
    print syntax.syntax
    sys.exit(1)

module_name = args["module"]
database_name = args["database"]
table_name = args.get("table-name")
sequence_name = args.get("sequence-name")

# Open the store.

s = sqltriples.open(database_name, module_name, table_name=table_name, sequence_name=sequence_name, debug=args.has_key("debug"))
try:

    # Initialise the database, if appropriate.

    if args.has_key("init"):
        s.init()
        s.commit()

    # Remove the database, if appropriate.

    elif args.has_key("delete"):
        s.delete()
        s.commit()

    # Show the contexts, if requested.

    elif args.has_key("contexts"):
        print s.contexts()

    # Remove the context, if specified.

    elif args.has_key("remove-context"):
        s.remove_context(args["remove-context"])
        s.commit()
        print "Context", args["remove-context"], "removed."

finally:
    s.close()

# vim: tabstop=4 expandtab shiftwidth=4
