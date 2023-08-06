# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from vellum.parser import parse, Reference
from nose.tools import *

def parse_file(file):
    f = open(file,'r')
    return parse('input', f.read())

def test_parse_input():
    spec = parse_file("build.vel")
    assert "targets" in spec
    assert "imports" in spec
    assert "depends" in spec
    assert "options" in spec

def test_parse_assignment():
    cases = [
            "random()",
            "targets(test 1)",
            "targets(test 2)\nstuff(test 3)"
            ]
    def parse_assigment(case):
        assert parse('input', case)
    for case in cases:
        yield parse_assigment, case

def test_parse_expr():
    cases = {
            "(test [1 2 3 4])": {'test' : [1,2,3,4]},
            "[1 2 3 4 5]": [1,2,3,4,5],
            "[(test 1) [1 2]]": [{'test': 1}, [1,2]],
            "12345": 12345,
            "'testing'": 'testing',
            "$ a shell\n": ' a shell\n',
            "yes": True,
            "no": False,
            '()':{},
            '[]':[],
            }

    for case, result in cases.items():
        p = parse("expr", case)
        assert_equal(p, result, "Expression %r did not parse to match, but was %r." % (case, result))

def test_parse_reference():
    cases = {
            "name1 'hi'": Reference("name1", 'hi'),
            "name3 [1 2 3]": Reference("name3", [1,2,3]),
            "name4 (test 1)": Reference("name4", {'test': 1}),
    }

    for case, compare in cases.items():
        res = parse('reference', case)
        assert res, "Reference %s did not parse." % case
        assert_equal(compare.name, res.name, "name %r should be %r" % (compare.name, res.name))
        assert_equal(compare.expr, res.expr, "name %r should be %r" % (compare.name, res.name))

def test_parse_flavors():
    cases = {
        '$ shell\n': '$',
        '| pipe\n': '|',
        '> gt\n': '>',
    }

    for case, compare in cases.items():
        res = parse('expr', case)
        assert_equal(res.flavor, compare, "flavor %s should be %s"%(res.flavor, compare))

def test_parse_structure_order():
    src = "(ab 1 bc 2 cd 3 de 4)"
    res = parse('expr', src)
    assert_equal(res.order, ['ab', 'bc', 'cd', 'de'])
