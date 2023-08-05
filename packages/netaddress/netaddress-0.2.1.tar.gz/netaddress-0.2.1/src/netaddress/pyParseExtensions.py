#!/usr/bin/env python2.4
"""
Copyright 2007, Vincent Kraeutler, all rights reserved.
See LICENSE for details.

A handful of useful extra combinators not present in pyparse.
"""

from pyparsing import alphas, And, Empty, Literal, nums, OneOrMore, Optional, Or, srange, Word, ZeroOrMore

def oneOf(r):
    return Word(r, exact = 1)

def oneOfRange(r):
    return oneOf(srange("[" + r + "]"))

def repeat(parser, n):
    
    if n < 0:
        raise ValueError, "Can't repeat less than zero times."
    
    if n == 0:
        # this should in principle never happen.
        return Empty()
    elif n == 1:
        return parser
    else:
        return parser + repeat(parser, n - 1)
    
def fromTo(parser, min = 0, max = 1):
    """
    @param min lower bound (inclusive)
    @param max upper bound (inclusive -- note this conforms with ABNF convention, but not the python one)
    
    This is an inefficient kludge. But it's getting late and I want to finish this.
    
    Behaves like pyparsing's Word, except you can use it to build delimited parsers
    out of simpler ones (instead of just out of characters).
    """
    if max < min:
        raise ValueError, "Upper bound lower than lower bound."
    options = [repeat(parser, ii) for ii in xrange(min, max + 1)]
    
    # return "largest" parser first:
    #options.reverse()
    return Or(options)

def upTo(parser, max = 1):
    return fromTo(parser, 0, max)

Char = oneOf(alphas)
Digit = oneOf(nums)
Number = Word(nums)
AlphaNum = Or([Char, Digit])
OneToNine = oneOfRange("1-9")
ZeroToFour = oneOfRange("0-4")
ZeroToFive = oneOfRange("0-5")
HexChars = oneOf("abcdef")