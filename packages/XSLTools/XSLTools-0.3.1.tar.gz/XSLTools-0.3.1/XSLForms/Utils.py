#!/usr/bin/env python

"""
Utility functions for XSLForms documents.

Copyright (C) 2005 Paul Boddie <paul@boddie.org.uk>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

def add_elements(positions, element_name, element_parent_name=None):

    """
    At the specified 'positions' in a document, add a new element of the given
    'element_name'. If the optional 'element_parent_name' is specified, ensure
    the presence of special parent elements bearing that name, adding them at
    the specified 'positions' where necessary, before adding the elements with
    the stated 'element_name' beneath such parent elements.
    """

    if not positions:
        return
    for position in positions:
        if element_parent_name:
            parent_elements = position.xpath(element_parent_name)
            if not parent_elements:
                parent_element = position.ownerDocument.createElementNS(None, element_parent_name)
                position.appendChild(parent_element)
            else:
                parent_element = parent_elements[0]
        else:
            parent_element = position
        parent_element.appendChild(position.ownerDocument.createElementNS(None, element_name))

def remove_elements(positions):

    """
    Remove the elements located at the given 'positions'.
    """

    if not positions:
        return
    for position in positions:
        position.parentNode.removeChild(position)

# vim: tabstop=4 expandtab shiftwidth=4
