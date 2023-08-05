"""pyfo_test - unit tests for pyfo

This file is part of the pyfo package.

Created and maintained by Luke Arno <luke.arno@gmail.com>

See documentation of pyfo method in this module for details.

Copyright (C) 2006  Central Piedmont Community College

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
import os, unittest
from pyfo import pyfo

def makenewtest(name, infile, args, kw, expectedfile, message):
    """Create a test method for a given test rule."""
    def newtest(self):
        exf = file(os.sep.join([self._expect_dir, expectedfile]))
        inf = file(os.sep.join([self._input_dir, infile]))
        struct = eval(inf.read())
        expectation = exf.read()
        exf.close(); inf.close()
        try:
            assert pyfo(struct, *args, **kw) == expectation
        except AssertionError, ae:
            raise AssertionError(
                    "Test %s did not result in expected output.\n\n%s"  
                        % (name, message))
    newtest.__doc__ = "Generated method for rule '%s'" % name
    return newtest

class MakeTests(type):
    """Build TestCase based on rules."""
    def __init__(cls, name, bases, dct):
        """Attach a test method for each rule in cls._comparisons."""
        [setattr(cls, 
                 "test_"+name, 
                 makenewtest(name, infile, args, kw, expectedfile, message)) 
         for name, infile, args, kw, expectedfile, message
         in cls._compairisons]
        super(MakeTests, cls).__init__(name, bases, dct)
    def gen_expectations(cls):
        """Generate expected output from know working code and test input."""
        print "generating tests: "
        for name, infile, args, kw, expectedfile, message in cls._compairisons:
            exf = file(os.sep.join([cls._expect_dir, expectedfile]), 'w')
            inf = file(os.sep.join([cls._input_dir, infile]))
            struct = eval(inf.read())
            exf.write(pyfo(struct, *args, **kw))
            exf.close(); inf.close()
            print " . generating:", name
        print " done"

class LoadAndCompare(unittest.TestCase):
    """Leverage metaclass to generate methods based on test rules.
    
    Use 'test_rules' file, 'test-input' dir, and 'expectations' dir
    """
    __metaclass__ = MakeTests
    _expect_dir = 'expectations'
    _input_dir = 'test-input'
    _compairisons = eval(file('test_rules').read())

class OrderedLoader(unittest.TestLoader):
    """Tests need to run in order."""
    def getTestCaseNames(self, testCaseClass):
        """Return test name in order of rules they are gened from."""
        if testCaseClass.__name__ == 'LoadAndCompare':
            return ["test_"+c[0] for c in LoadAndCompare._compairisons]
        else:
            return super(unittest.TestLoader, 
                         self).getTestCaseNames(testCaseClass)

if __name__ == '__main__':
    import sys
    if sys.argv[1:2] == ['gen']:
        LoadAndCompare.gen_expectations()
    elif sys.argv[1:2] == ['run']:
        del sys.argv[1]
        unittest.main(testLoader=OrderedLoader())
    else:
        print """
python2.4 pyfo_test.py gen

   generate expectations from a known working pyfo

python2.4 pyfo_test.py run

   run unit tests
        """

