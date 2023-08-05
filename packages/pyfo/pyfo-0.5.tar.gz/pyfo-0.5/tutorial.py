#!/usr/bin/env python2.4
"""tutorial - a quick example of using pyfo.

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
# pyfo provides a method called pyfo. I should not have named them
# both the same but I did. The signature looks like this:

# def pyfo(node, prolog=False, pretty=False, indent_size=2, encoding='utf-8')

# Node can be any number of things. Most often it will be a tuple shaped like
# this:

# ('elementname', node_or_child_nodes, {'attr':'value'})

# The dict of attributes is optional:

# ('elementname', node_or_child_nodes)

#A node can also be most any other type and should usually do what you might
# expect.

# One good example is worth a hundred pages of description.
# So, lets say you have some data that you need to turn into XML:

from pyfo import pyfo

test_input = \
('root', 
 [('string','hello'), 
  ('float', 3.14),
  ('int', 5),
  ('unicode', u'this is unicode: \u221e'),
  ('list', [('node', 'hello'), '<raw-node message="hello"/>']),
  ('dictionary', dict(parrot='dead', spam='eggs')),
  ('generator', (('node', x) for x in range(6))),
  ('tuple', ('one', 'two')),
  ('None', None),
  ('int-zero', 0),
  ('float-zero', 0.0),
  ('empty-string', ""),
  ('object', type('obj', (), dict(__repr__=lambda s: "object repr"))()),
  ('func', lambda: 'this is a func'),
  ('escaping', ' > < & ')])

# pyfo returns a unicode object so if you are going to output to an ascii
# terminal you should do something like this:

result = pyfo(test_input, pretty=True, prolog=True, encoding='ascii')
print result.encode('ascii', 'xmlcharrefreplace')

# You could try to print the result directly if you are using all ascii
# characters but that is usually a pretty bad assumptions to make.

# Your output should look like this:

'''
<?xml version="1.0" encoding="ascii"?>
<root>
  <string>hello</string>
  <float>3.14</float>
  <int>5</int>
  <unicode>this is unicode: &#8734;</unicode>
  <list>
    <node>hello</node>
    <raw-node message="hello"/>
  </list>
  <dictionary>
    <parrot>dead</parrot>
    <spam>eggs</spam>
  </dictionary>
  <generator>
    <node>0</node>
    <node>1</node>
    <node>2</node>
    <node>3</node>
    <node>4</node>
    <node>5</node>
  </generator>
  <tuple>
    <one>two</one>
  </tuple>
  <None/>
  <int-zero>0</int-zero>
  <float-zero>0.0</float-zero>
  <empty-string/>
  <object>object repr</object>
  <func>this is a func</func>
  <escaping> &gt; &lt; &amp; </escaping>
</root>
'''

