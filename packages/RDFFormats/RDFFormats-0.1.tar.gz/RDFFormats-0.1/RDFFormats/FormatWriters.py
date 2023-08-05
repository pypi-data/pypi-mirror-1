#!/usr/bin/env python

"""
Format writer classes.

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

class DOMWriter:

    "A DOM document writer."

    def __init__(self, doc, root, qualifier, value_as_attribute=0):

        """
        Initialise the writer with the document 'doc' to be written to, the
        element 'root' within which information is to be inserted. The following
        parameters configure the writer:

          * qualifier           - use a specific qualifier, given as a 2-tuple
                                  of the form (namespace, prefix), on elements
                                  added to the document
          * value_as_attribute  - write values as attributes on elements (or
                                  write them as text within the elements, as is
                                  the default, false value for this parameter)
        """

        self.doc = doc
        self.context = root
        self.ns, self.prefix = qualifier
        self.value_as_attribute = value_as_attribute

    def start_element(self, label):
        element = self.doc.createElementNS(self.ns, self.prefix + self.get_item_type_name(label))
        self.context.appendChild(element)
        self.context = element

    def end_element(self, label):
        assert self.context.localName == self.get_item_type_name(label)
        self.context = self.context.parentNode

    def write_attribute(self, name, modifiers=None, value=None, subvalues=None, multivalues=None):
        property_name = self.get_property_name(name)
        element = self.doc.createElementNS(self.ns, self.prefix + property_name)
        self.context.appendChild(element)

        if modifiers is not None:
            for modifier_name, modifier_value in modifiers:
                element.setAttributeNS(None, modifier_name.lower(), modifier_value)

        if value is not None:
            if self.value_as_attribute:
                element.setAttributeNS(None, self.get_property_label(property_name) or "details", value)
            else:
                element.appendChild(self.doc.createTextNode(value))

        elif subvalues is not None:
            for subvalue_name, subvalue_value in subvalues:
                subelement = self.doc.createElementNS(self.ns, self.prefix + subvalue_name.lower())
                element.appendChild(subelement)
                if self.value_as_attribute:
                    subelement.setAttributeNS(None, self.get_property_label(property_name) or "details", subvalue_value)
                else:
                    subelement.appendChild(self.doc.createTextNode(subvalue_value))

        elif multivalues is not None:
            for multivalue in multivalues:
                subelement = self.doc.createElementNS(self.ns, self.prefix + "value")
                element.appendChild(subelement)
                if self.value_as_attribute:
                    for multivalue_name, multivalue_value in multivalue.items():
                        subelement.setAttributeNS(None, multivalue_name.lower(), multivalue_value)
                else:
                    first = 1
                    for multivalue_name, multivalue_value in multivalue.items():
                        if not first:
                            s = "/" + multivalue_value
                        else:
                            s = multivalue_value
                        subelement.appendChild(self.doc.createTextNode(s))
                        first = 0

    def close(self):
        pass

    def get_item_type_name(self, label):
        raise NotImplementedError, "get_item_type_name"

    def get_property_name(self, attribute_name):
        raise NotImplementedError, "get_property_name"

    def get_property_label(self, property_name):
        raise NotImplementedError, "get_property_label"

# vim: tabstop=4 expandtab shiftwidth=4
