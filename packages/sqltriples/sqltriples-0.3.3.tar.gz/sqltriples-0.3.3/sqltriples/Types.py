#!/usr/bin/env python

"""
Special data types inheriting from the unicode type in order to provide
interoperability with rdflib.

Copyright (C) 2006, 2007 Paul Boddie <paul@boddie.org.uk>

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

# Special type classes.

class Special(unicode):

    "A special abstract class inheriting from the unicode type."

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, unicode.__repr__(self))

class URIRef(Special):

    "An URI reference compatible with the rdflib class of the same name."

    pass

class Literal(Special):

    "A literal compatible with the rdflib class of the same name."

    pass

class Namespace(URIRef):

    "A namespace compatible with the rdflib class of the same name."

    def __getitem__(self, item):
        try:
            return unicode(self)[item]
        except TypeError:
            return Namespace(self + item)

class BNode:

    "A BNode compatible with the rdflib class of the same name."

    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.value))

    def __unicode__(self):
        return self.value

    def __eq__(self, other):
        return hasattr(other, "value") and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # NOTE: Should probably be more careful to avoid collisions with non-BNodes.
        return hash(self.value)

# Special expression classes.

class AbstractExpression:

    "An abstract expression class providing tuple infrastructure."

    def __len__(self):
        return 2

    def __getitem__(self, i):
        return (self.get_expression(), self.values)[i]

class Expression(AbstractExpression):

    "An general class wrapping an expression and associated values."

    # NOTE: Improve the value type mechanism.

    def __init__(self, expr, values, value_type="L"):

        """
        Initialise the expression with the 'expr' string and a sequence of
        'values', optionally indicating the expression's 'value_type' ('L' for
        Literal, 'U' for URIRef).
        """

        self.expr = expr
        self.values = values
        self.value_type = value_type

    def get_expression(self):
        return self.expr

class URIRefExpression(Expression):

    "An expression acting as a URIRef."

    def __init__(self, expr, values):
        Expression.__init__(self, expr, values, "U")

class LiteralExpression(Expression):

    "An expression acting as a Literal."

    def __init__(self, expr, values):
        Expression.__init__(self, expr, values, "L")

# Special pattern and value classes.

class Pattern:

    "A pattern which may be unpacked like a tuple."

    def __init__(self, subject, predicate, object):
        self.subject = subject
        self.predicate = predicate
        self.object = object

    def __len__(self):
        return 3

    def __getitem__(self, i):
        return (self.subject, self.predicate, self.object)[i]

class Defined:

    "A class indicating a value defined for a particular relation."

    pass

# Useful defaults.

RDFNS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
TYPE = RDFNS["type"]
ALL = (None, None, None)

# vim: tabstop=4 expandtab shiftwidth=4
