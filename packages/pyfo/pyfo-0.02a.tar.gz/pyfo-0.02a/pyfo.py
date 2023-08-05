"""pyfo - Generate XML using native python data structures.

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

import types
import re

# this bit adapted from O'Reilly Python Cookbook
edict = {'&':'&amp;', '<':'&lt;','>':'&gt;'}
rx = re.compile('|'.join(map(re.escape, edict)))
xlat = lambda match: edict[match.group(0)]

def escape(astr):
    """Escape entities for XML."""
    return rx.sub(xlat, astr)

def make_attributes(dct):
    """Turn a dict into string of XML attributes."""
    return "".join((' %s="%s"' % (x, escape(str(y))) 
                    for x, y in dct.iteritems()))

def pyfo(node, prolog=False, pretty=False, indent_size=2):
    """Generate XML using native python data structures.
   
    node structure like (name, contents) or (name, contents, attribs)
    accepts stings, callables, or another node structure.
   
    pyfo should be called with a tuple of two or three items like so:
    (element, contents, attributes) or a string.

    for a tuple:
    
        the first item:
            is the element name.
  
        the second item:
            if it is callable, it is called 
            and its return value .
    
            if it is a list, pyfo is called on all its members 
            and the results are concatenated to become the contents.

            otherwise it is run through 'str' and 'escape'.
    
        optional third item: 
            should be a dictionary used as xml attributes
    
    for a string:
        
        just return it.
    """
    if callable(node):
        node = node()
    if not node:
        return ""
    if pretty and pretty >= 0:
        if pretty is True: pretty = 1
        indent = '\n' + (" " * indent_size * pretty)
        unindent = '\n' + (" " * indent_size * (pretty-1))
        pretty += 1
    else:
        unindent = indent = ""
    if isinstance(node, basestring):
        return node
    elif len(node) == 2:
        name, contents = node
        dct = {}
    else:
        name, contents, dct = node
    leaf = False
    if callable(contents):
        contents = contents()
        leaf = True
    if isinstance(contents, dict):
        contents = contents.items()
    # How can this catch more iterables?
    if type(contents) in [types.ListType, types.GeneratorType]:
        cgen = (pyfo(c, pretty=pretty, indent_size=indent_size) 
                for c in contents)
        contents = indent.join((c for c in cgen if c))
    elif type(contents) is types.TupleType:
        contents = pyfo(contents, pretty=pretty, indent_size=indent_size)
    elif contents not in [None, ""]:
        contents = escape(str(contents))
        leaf = True
    if leaf:
        indent = unindent = ""
    prolog = prolog and '<?xml version="1.0"?>\n' or ''
    if contents:
        return '%s<%s%s>%s%s%s</%s>' % (prolog, 
                                        name, 
                                        make_attributes(dct), 
                                        indent,
                                        contents, 
                                        unindent,
                                        name)
    else:
        return '%s<%s%s/>' % (prolog, 
                              name, 
                              make_attributes(dct))

