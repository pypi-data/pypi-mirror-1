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

    print "Test addition, literal/string equivalence, removal."

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

    print "--------"
    print "Test addition, matching, ordering, expressions, expressions plus ordering."

    s.add(("p", "q", Literal("20050101")))
    s.add(("p", "q", Literal("20050401")))
    s.add(("p", "q", Literal("20051001")))
    s.add(("p", "q", Literal("20060101")))
    result = s.triples(("p", "q", None))
    print "Should be 4 triples:", len(result) == 4
    print result
    print
    result = s.triples(("p", "q", None), ordering="desc")
    print "Should be 4 triples (in descending order):", len(result) == 4
    print result
    print
    result = s.triples(("p", "q", ("_ > ? and _ < ?", ["20050301", "20051101"])))
    print "Should be 2 triples:", len(result) == 2
    print result
    print
    result = s.triples(("p", "q", ("_ > ? and _ < ?", ["20050301", "20051101"])), ordering="asc")
    print "Should be 2 triples (in order):", len(result) == 2
    print result
    print

    print "--------"
    print "Test subjects, addition and deletion using subjects, chaining, and"
    print "widening."

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
    s.add((URIRef("N1"), URIRef("O1"), "p"))
    s.add((URIRef("N2"), URIRef("O2"), "q"))
    result = s.triples((None, None, subject))
    print "Should be 1 result:", len(result) == 1
    print result
    print
    result = s.triples((subject, None, None))
    print "Should be 4 results:", len(result) == 4
    print result
    print
    s.remove((None, [URIRef("O1"), URIRef("O2")], None))
    del subject["q"]
    result = subject["q"]
    print "Should be 0 results:", len(result) == 0
    print result
    print

    print "--------"
    print "Test BNode creation and deletion."

    s.add((URIRef("xyz"), URIRef("abc"), BNode()))
    s.add((URIRef("xyz"), URIRef("abc"), BNode()))
    result = s.triples((URIRef("xyz"), None, None))
    print "Should be 2 triples:", len(result) == 2
    print "Should use distinct objects:", len(result) ==2 and result[0][2] != result[1][2]
    print result
    print
    s.remove((URIRef("xyz"), None, None))

    print "--------"
    print "Test range comparisons, predicates, usage of predicates in patterns."

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
    result = s.and_triples([t1, t2])
    print "Should be 2 triples:", len(result) == 2
    print result
    print
    p1 = s.predicates(URIRef("a"))
    result = s.and_triples([p1, t1, t2])
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

    print "--------"
    print "Test subjects, subjects plus expressions."

    subjects_with_predicate_b = s.subjects(URIRef("b"))
    print "Should be 1 result:", len(subjects_with_predicate_b) == 1
    print subjects_with_predicate_b
    print
    subjects_with_object_gt_2 = s.subjects(None, ("_ > ?", [Literal("2")]))
    print "Should be 2 results:", len(subjects_with_object_gt_2) == 2
    print subjects_with_object_gt_2
    print

    print "--------"
    print "Test negations of subjects."

    triples_for_subjects_not_with_predicate_b = s.not_triples(subjects_with_predicate_b)
    print "Should be 6 results:", len(triples_for_subjects_not_with_predicate_b) == 3
    print triples_for_subjects_not_with_predicate_b
    print

    print "--------"
    print "Test of expression as object plus negation."

    triples_for_subjects_not_with_object_gt_2 = s.not_triples(s.subjects(None, ("_ > ?", [Literal("2")])))
    print "Should be 0 results:", len(triples_for_subjects_not_with_object_gt_2) == 0
    print triples_for_subjects_not_with_object_gt_2
    print

    print "--------"
    print "Test of presence."

    has_b = s.triples((None, URIRef("b"), s.Defined()))
    print "Should be 3 results:", len(has_b) == 3
    print has_b
    print

    print "--------"
    print "Test of absence."

    not_has_b = s.not_triples(s.triples((None, URIRef("b"), s.Defined())))
    print "Should be 6 results:", len(not_has_b) == 6
    print not_has_b
    print

    print "--------"
    print "Test of subject combination."

    triples_for_subjects_b_obj_gt_2 = s.triples(expression=s.and_subjects([subjects_with_predicate_b, subjects_with_object_gt_2]))
    print "Should be 6 triples:", len(triples_for_subjects_b_obj_gt_2) == 6
    print triples_for_subjects_b_obj_gt_2
    print

    print "--------"
    print "Test of triple combination."

    triples_for_subjects_b_obj_gt_2 = s.and_triples([subjects_with_predicate_b, subjects_with_object_gt_2])
    print "Should be 6 triples:", len(triples_for_subjects_b_obj_gt_2) == 6
    print triples_for_subjects_b_obj_gt_2
    print

    print "--------"
    print "Test of triple combination using intersections."

    subjects_b_obj_gt_2 = s.intersect_subjects([subjects_with_predicate_b, subjects_with_object_gt_2])
    print "Should be 1 subject:", len(subjects_b_obj_gt_2) == 1
    print subjects_b_obj_gt_2
    print

    print "--------"
    print "Test of triple combination using conjunctions and negations."

    triples_with_predicate_x_obj_gt_2 = s.and_triples([s.not_triples(subjects_with_predicate_b), subjects_with_object_gt_2])
    print "Should be 3 triples:", len(triples_with_predicate_x_obj_gt_2) == 3
    print triples_with_predicate_x_obj_gt_2
    print

    print "--------"
    print "Test of triple combination."

    triples_a = ordered_triples_b_obj_gt_2 = s.triples(expression=s.and_triples([subjects_with_predicate_b, subjects_with_object_gt_2]), ordering="asc")
    print "Should be 6 triples (in order):", len(ordered_triples_b_obj_gt_2) == 6
    print ordered_triples_b_obj_gt_2
    print

    print "--------"
    print "Test of triple combination."

    ordered_triples_x_gt_2 = s.triples((None, URIRef("x"), None),
        expression=s.and_triples([subjects_with_predicate_b, subjects_with_object_gt_2]), ordering="asc")
    print "Should be 3 triples (in order):", len(ordered_triples_x_gt_2) == 3
    print ordered_triples_x_gt_2
    print

    print "--------"
    print "Test of tuples and ordering."

    s.add((URIRef("c"), URIRef("p"), URIRef("a")))
    s.add((URIRef("c"), URIRef("q"), URIRef("a")))
    s.add((URIRef("d"), URIRef("p"), URIRef("a")))
    s.add((URIRef("d"), URIRef("p"), URIRef("b")))
    ordered = s.tuples((None, URIRef("p"), URIRef("x"), None), ordering="asc")
    print "Should be 8 tuples (in order):", len(ordered) == 8
    print ordered
    print

    print "--------"
    print "Test of tuples and chaining."

    s.add((URIRef("B"), URIRef("C"), URIRef("c")))
    s.add((URIRef("c"), URIRef("E"), URIRef("d")))
    chained = s.tuples((None, URIRef("C"), URIRef("E"), ordered))
    print "Should be 1 tuple:", len(chained) == 1
    print chained
    print
    extended = s.tuples(chained.pattern[:-1] + ordered.pattern[1:])
    print "Should be 5 tuples:", len(extended) == 5
    print extended
    print

    print "--------"
    print "Test of negation with tuples."

    all_tuples = s.tuples((None, None, None, None))
    negated = s.not_tuples(chained, (None, None, None, None))
    print "Should be all but one of the tuples:", len(negated) == len(all_tuples) - 1
    print negated
    print

    print "--------"
    print "Test of triples as object."

    triples_p_a = s.triples((None, URIRef("p"), triples_a), ordering="asc")
    print "Should be 2 triples (in order):", len(triples_p_a) == 2
    print triples_p_a
    print
    print "Should have had 6 triples before:", len(triples_a) == 6
    print triples_a
    print

    s.remove((URIRef("c"), URIRef("p"), URIRef("a")))
    s.remove((URIRef("c"), URIRef("q"), URIRef("a")))
    s.remove((URIRef("d"), URIRef("p"), URIRef("a")))
    s.remove((URIRef("d"), URIRef("p"), URIRef("b")))
    subject_a = s.subject(URIRef("a"))

    print "--------"
    print "Test of triple combination."

    result = s.triples(expression=s.and_triples([t2, subject_a]))
    print "Should be 3 triples:", len(result) == 3
    print result
    print

    print "--------"
    print "Test of triple combination using expressions."

    result = s.triples(expression=s.or_triples([t2, subject_a]))
    print "Should be 9 triples:", len(result) == 9
    print result
    print

    print "--------"
    print "Test of triple combination."

    t1_and_t2 = s.count(expression=s.and_triples([t1, t2]))
    print "Should be 2:", len(t1_and_t2) == 2
    print len(t1_and_t2)
    print
    s.add((URIRef("c"), URIRef("y"), URIRef("a")))
    result = s.triples((None, None, t2))
    print "Should be 1 triple:", len(result) == 1
    print result
    print
    result = s.triples((None, None, subjects_with_object_gt_2))
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
