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

from pyParseExtensions import *
from pyparsing import Group, Combine


# Begin RFC 3986 

HEXDIG = Digit ^ HexChars

unreserved = AlphaNum ^ oneOf("-._~")
sub_delims = Or(oneOf("!$&'()*+,;="))

pct_encoded = Literal("%") + repeat(HEXDIG, 2) 
pchar = unreserved ^ pct_encoded ^ sub_delims ^ ":" ^ "@"

query = ZeroOrMore(pchar ^ "/" ^"?")
fragment = query

SchemeChars = Or([AlphaNum, Or(oneOf("+-."))])
scheme = Combine(Char + OneOrMore(SchemeChars)).setResultsName("scheme")

userinfo = Combine(ZeroOrMore(unreserved ^ pct_encoded ^ sub_delims ^ ":")).setResultsName("userinfo")

# it is my understanding that pyparsing is lazy -- we need to change the order here, 
# so it tests the longest first. YES?
dec_octet = Combine(Or([
        Literal("25") + ZeroToFive,            # 250 - 255
        Literal("2") + ZeroToFour + Digit,     # 200 - 249
        Literal("1") + repeat(Digit, 2),       # 100 - 199
        OneToNine + Digit,                     # 10 - 99
        Digit                                  # 1-9    
        ]))
IPv4address = Group(repeat(dec_octet + Literal("."), 3) + dec_octet)

dunno = unreserved ^ sub_delims ^ ":"
IPvFuture  = Literal("v") + OneOrMore(HEXDIG) + "." + OneOrMore(dunno)

h16 = Combine(fromTo(HEXDIG, 1, 4))
h16Col = h16 + ":"
Colh16 = ":" + h16 
ls32 = Or([h16Col + h16 , IPv4address])
IPv6address = Group(Or([
                  repeat(h16Col, 6) + ls32,
                  Literal("::") + repeat(h16Col, 5) + ls32,
                  Optional(h16) + Literal("::") + repeat(h16Col, 4) + ls32,
                  Optional(upTo(h16Col, 1) + h16) + Literal("::") + repeat(h16Col, 3) + ls32,
                  Optional(upTo(h16Col, 2) + h16) + Literal("::") + repeat(h16Col, 2) + ls32,
                  Optional(upTo(h16Col, 3) + h16) + Literal("::") + h16Col + ls32,
                  Optional(upTo(h16Col, 4) + h16) + Literal("::") + ls32,
                  Optional(upTo(h16Col, 5) + h16) + Literal("::") + h16,
                  Optional(upTo(h16Col, 6) + h16) + Literal("::")
                  ])).setResultsName("IPv6address")
IP_literal = Group(
                   Literal("[") + Or([IPv6address, IPvFuture]) + Literal("]")
                   ).setResultsName("IP_literal")
reg_name = Combine(ZeroOrMore(unreserved ^ pct_encoded ^ sub_delims))
host = IP_literal ^ IPv4address ^ reg_name
host.setResultsName("host")

port = Number.setResultsName("port")
authority = Group(
        Optional(userinfo + "@") + host + Optional(Literal(":") + port)
    ).setResultsName("authority")

segment = Combine(ZeroOrMore(pchar))
segment_nz = Combine(OneOrMore(pchar))
segment_nz_nc = Combine(OneOrMore(unreserved ^ pct_encoded ^ sub_delims ^ "@"))
sepSegment = Literal("/") + segment
path_abempty = ZeroOrMore(sepSegment).setResultsName("path_abempty")
path_absolute = Literal("/") + Optional(segment_nz + path_abempty)
path_noscheme = segment_nz_nc + ZeroOrMore(sepSegment)
path_empty = Literal("")

hier_part = Group(
            Group(Literal("//") + authority + path_abempty) ^ \
            path_absolute ^ \
            path_noscheme ^ \
            path_empty
            ).setResultsName("hier_part")

URI = scheme + ":" + hier_part + Optional("?" + query) + Optional("#" + fragment)

# End RFC 3986 
