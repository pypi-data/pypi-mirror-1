#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"Test program."

import sqltriples
import cmdsyntax
import sys

URIRef, Literal, BNode = sqltriples.URIRef, sqltriples.Literal, sqltriples.BNode

syntax = cmdsyntax.Syntax("""
    --database=DATABASE_NAME
    --module=MODULE_NAME
    [ --context=CONTEXT_NAME ]
    [ --table-name=TABLE_NAME ]
    [ --sequence-name=SEQUENCE_NAME ]
    [ --debug ]
    [ --commit ]
    [ --no-test ]
    """)

syntax_matches = syntax.get_args(sys.argv[1:])

try:
    args = syntax_matches[0]
except IndexError:
    print "Use the --database option to indicate which database is being altered."
    print "Use the --module option to indicate which kind of database system is being used."
    print "(Try PgSQL or pysqlite2.)"
    print "Optional arguments:"
    print "Use the --table-name option to specify the table in which triple store information is deposited."
    print "Use the --sequence-name option to specify the sequence from which BNode identifiers are obtained."
    print "(By default, 'triples' is used as the table name; 'bnode' is used as the sequence name.)"
    print "Use the --context option to specify a specific context (as opposed to no context)."
    print "Specify --debug to show the underlying SQL operations."
    print "Specify --commit to commit stored data afterwards."
    print "Specify --no-test to not run the test program and to keep the connection open afterwards."
    print "(This is useful for interactive mode investigations.)"
    print syntax.syntax
    sys.exit(1)

module_name = args["module"]
database_name = args["database"]
table_name = args.get("table-name")
sequence_name = args.get("sequence-name")

# Open the store.

s = sqltriples.open(database_name, module_name, table_name=table_name, sequence_name=sequence_name, debug=args.has_key("debug"))

# Get the context, if specified.

if args.has_key("context"):
    s = s.get_context(args["context"])

# Test the store.

if not args.has_key("no-test"):
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
    s.add((URIRef("xyz"), URIRef("abc"), BNode()))
    result = s.triples((URIRef("xyz"), None, None))
    print "Should be 2 triples:", len(result) == 2
    print "Should use distinct objects:", len(result) ==2 and result[0][2] != result[1][2]
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

if args.has_key("commit"):
    s.commit()

# Close the store (and the connection) if requested.

if not args.has_key("no-test"):
    s.close()

# vim: tabstop=4 expandtab shiftwidth=4
