"""test_wrapper - wrapper for unit tests for pyfo

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
import pyfo_test

def get_suite():
    """Return a Test Suite for use by setuptools."""
    ol = pyfo_test.OrderedLoader()
    return ol.loadTestsFromModule(pyfo_test)

