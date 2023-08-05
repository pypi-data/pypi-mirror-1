"""pyfo_test - unit tests for pyfo

This file is part of the pyfo package.

Created and maintained by Luke Arno <luke.arno@gmail.com>

See documentation of pyfo method in this module for details.

Copyright (C) 2006-2007  Central Piedmont Community College

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.

Central Piedmont Community College
1325 East 7th St.
Charlotte, NC 28204, USA

Luke Arno can be found at http://lukearno.com/
"""
import os
from unittest import FunctionTestCase, TestSuite, TextTestRunner
from difflib import unified_diff
from pyfo import pyfo


# basic info needed for this thing to run
expect_dir = 'expectations'
input_dir = 'test-input'
rules = eval(file('test_rules').read())


def make_test(name, infile, args, kw, expectedfile, message):
    """Create a test method for a given test rule."""
    def test_func():
        exf = file(os.sep.join([expect_dir, expectedfile]))
        inf = file(os.sep.join([input_dir, infile]))
        struct = eval(inf.read())
        expectation = exf.read()
        exf.close(); inf.close()
        result = pyfo(struct, *args, **kw)
        result = result.encode('utf-8', 'xmlcharrefreplace')
        try:
            assert result == expectation
        except AssertionError, ae:
            result = result.splitlines(True)
            expectation = expectation.splitlines(True)
            raise AssertionError(
                    "Test %s did not result in expected output.\n\n%s\n\n%s"  
                        % (name, 
                           message, 
                           "".join(unified_diff(result, expectation))))
    test_func.__doc__ = "Generated method for rule '%s'" % name
    test_func.__name__ = name
    return test_func


def generate_expected_output():
    """Generate expected output from know working code and test input."""
    print "generating tests: "
    for name, infile, args, kw, expectedfile, message in rules:
        exf = file(os.sep.join([expect_dir, expectedfile]), 'w')
        inf = file(os.sep.join([input_dir, infile]))
        struct = eval(inf.read())
        out = pyfo(struct, *args, **kw)
        exf.write(out.encode('utf-8', 'xmlcharrefreplace'))
        exf.close(); inf.close()
        print " . generating:", name
    print " done"


def gen_tests():
    """Generate a test function for each rule."""
    for name, infile, args, kw, expectedfile, message in rules:
        yield make_test(name, infile, args, kw, expectedfile, message) 


def suite():
    """Create test suite for functions fro gen_tests"""
    return TestSuite((FunctionTestCase(fn) for fn in gen_tests()))


if __name__ == '__main__':
    import sys
    if sys.argv[1:2] == ['gen']:
        generate_expected_output()
    elif sys.argv[1:2] == ['run']:
        TextTestRunner(suite()).run()
    else:
        print """
python2.4 pyfo_test.py gen

   generate expectations from a known working pyfo

python2.4 pyfo_test.py run

   run unit tests
        """

