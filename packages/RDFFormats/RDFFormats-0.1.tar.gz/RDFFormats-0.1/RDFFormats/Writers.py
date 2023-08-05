#!/usr/bin/env python

"""
Writer classes.

Copyright (C) 2006 Paul Boddie <paul@boddie.org.uk>

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

class Writer:

    """
    A writer class which, acting as a visitor on nodes in a store, employs a
    format writer in order to produce actual output.
    """

    def __init__(self, format_writer):
        self.format_writer = format_writer

    def write(self, store, node):

        """
        Write, using the 'store', the resource rooted at the given 'node'.
        """

        node_type = store.get_node_type(node)
        if node_type is not None and store.get_label(node_type) is not None:
            self.write_element(store, node, node_type)

    def write_element(self, store, node, node_type):

        """
        Write the element found in the 'store' represented by the given 'node'
        and having the given 'node_type'.
        """

        element_name = store.get_element_name(node_type)
        self.format_writer.start_element(element_name)

        # Check for UIDs.

        if isinstance(node, store.URIRef):
            uid_or_uriref = store.get_uid(node) or node
            self.write_uid(uid_or_uriref)

        # NOTE: This may not be entirely desirable - whilst BNode identifiers
        # NOTE: give an element of uniqueness, they don't always provide
        # NOTE: information about the system they came from.
        # NOTE:
        # NOTE: elif isinstance(node, store.BNode):
        # NOTE:     self.format_writer.write_attribute("UID", value=node)

        contents = []
        for subject, predicate, object in store.store.triples((node, None, None)):
            if predicate == store.ns["contains"]:
                contents.append((subject, predicate, object))
            elif predicate == store.ns["name"]:
                pass
            elif predicate != store.TYPE:
                attribute_name = store.get_attribute_name(predicate)
                if self.is_attribute_permitted(attribute_name, element_name):
                    self.write_attribute(store, attribute_name, object)
                elif attribute_name is None:
                    # Not part of the serialised data.
                    pass
                else:
                    raise ValueError, (element_name, attribute_name)

        for s, p, object in contents:
            for subject, predicate, subelement_type in store.store.triples((object, store.TYPE, None)):
                subelement_name = store.get_element_name(subelement_type)
                if self.is_element_permitted(subelement_name, element_name):
                    self.write_element(store, object, subelement_type)
                    break

        self.format_writer.end_element(element_name)

    def is_element_permitted(self, subelement_name, element_name):
        raise NotImplementedError, "is_element_permitted"

    def is_attribute_permitted(self, attribute_name, element_name):
        raise NotImplementedError, "is_attribute_permitted"

# vim: tabstop=4 expandtab shiftwidth=4
