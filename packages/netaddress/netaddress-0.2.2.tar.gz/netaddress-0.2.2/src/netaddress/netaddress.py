#!/usr/bin/env python2.4
"""
Copyright 2007, Vincent Kraeutler, all rights reserved.
See LICENSE for details.

This is a set of validating parser combinators, based on pyparsing supporting (nearly) 
the full grammar of URI's as specified in RFC 3986.

It is essentially a translation from the ABNF found on http://rfc.net/rfc3986.html#p49
into pyparse syntax. We need to re-order the definitionas a bit, so that python is happy.

Specifically, the validating parsers for the following address schemes are provided (see
NOTE's for a few caveats):
-- Full URI parsing according to RFC 3986;
-- implying support for parsing partial URI's as well as various IP addressing schemes.

The spurious naming patterns employed in the RFC are retained as far as possible, for easy
comparison with the original grammar. Specifically, "-" is replaced by "_". Furthermore,
repeated grammar patterns (i.e. query vs. fragment and path_abempty vs. path_absolute) 
have been eliminated.

NOTE: At this point the code parses correctly, but it is entirely untested.

NOTE: Parsing of numerical IPv6 addresses is restricted to a subset of valid IPv6 addresses, 
because pyparsing lacks the ABNF *x operator.

NOTE: pyparsing will complain on 
   path_empty = Literal("")
and suggest the use of Empty() instead. This is not correct, since Empty always produces
a match, whereas we want to match for input termination.
"""

from rfc3986 import *
import notQuiteURI
