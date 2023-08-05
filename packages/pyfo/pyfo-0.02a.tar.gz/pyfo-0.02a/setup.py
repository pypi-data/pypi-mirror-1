"""setup - setuptools based setup for pyfo

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
from setuptools import setup

setup(name='pyfo',
      version='0.02a',
      description='Easily generate XML from Python data structures.',
      long_description=\
      "This package was developed by Luke Arno for "\
      +"Central Piedmont Community College in response to "\
      +"dissatisfaction with available alternatives for quickly "\
      +"generating XML. Concatenating strings is ugly and error "\
      +"prone, using OO APIs for XML is heavy and overkill for "\
      +"generating simple XML output.",
      author='Luke Arno',
      author_email='luke.arno@gmail.com',
      url='http://foss.cpcc.edu/pyfo/',
      license="GPL2",
      py_modules=['pyfo'],
      packages = [],
      test_suite='test_wrapper.get_suite',
      keywords="xml html",
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Text Processing :: Markup :: XML',
                   'Topic :: Text Processing :: Markup :: HTML',
                   'Topic :: Utilities'])
