#!/usr/bin/env python

"Test sqlliterals."

import sqlliterals.pyparser
import sqlliterals.regexp

def show(regions):
    non_literal = 1
    for region in regions:
        print region,
        if non_literal:
            print "(NL)",
        else:
            print "(L)",
        non_literal = not non_literal
    print

l = [
    "a = a",
    "a = 'a'",
    "'a' = a",
    "'a' = 'a'",
    "a = ''''",
    "'''' = a",
    "'''' = ''''",
    "a = '''a'''",
    "'''a''' = a",
    "'''a''' = '''a'''"
    ]

for s in l:
    show(sqlliterals.pyparser.parseString(s))
    show(sqlliterals.regexp.parseString(s))

# vim: tabstop=4 expandtab shiftwidth=4
