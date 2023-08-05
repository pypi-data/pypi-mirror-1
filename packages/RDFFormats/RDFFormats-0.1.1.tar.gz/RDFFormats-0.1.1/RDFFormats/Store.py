#!/usr/bin/env python

"""
Storage of nodes according to general RDFFormats conventions.

Copyright (C) 2006, 2007 Paul Boddie <paul@boddie.org.uk>

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

from RDFFormats.Format import *

class AbstractStore:

    "The interface employed by the RDFCalendar.Parsers classes."

    def has_item(self, uriref):
        raise NotImplementedError, "has_item"
    def add_node(self, label, uriref=None):
        raise NotImplementedError, "add_node"
    def add_name(self, node, name):
        raise NotImplementedError, "add_name"
    def add_contains(self, node, element):
        raise NotImplementedError, "add_contains"

class AbstractHandler:

    "WebOrganiser-compatible handler methods."

    def remove_node(self, node):
        raise NotImplementedError, "remove_node"

    def get_urirefs_for_item_type(self, item_type_name):
        raise NotImplementedError, "get_urirefs_for_item_type"

    def get_urirefs_for_property_type(self, property_type_name):
        raise NotImplementedError, "get_urirefs_for_property_type"

    def get_urirefs_for_attribute(self, attribute):
        raise NotImplementedError, "get_urirefs_for_attribute"

    def supports_item_type(self, item_type_str):
        raise NotImplementedError, "supports_item_type"

    def get_supported_item_types(self):
        raise NotImplementedError, "get_supported_item_types"

    def write_to_stream(self, stream, main_node=None, nodes=None, *args, **kw):
        raise NotImplementedError, "write_to_stream"

    def write_to_document(self, doc, root, main_node=None, nodes=None, qualifier=None, value_as_attribute=0):
        raise NotImplementedError, "write_to_document"

    def parse(self, f, name=None, uriref=None):
        raise NotImplementedError, "parse"

    def parse_document_fragment(self, doc, root, uriref=None):
        raise NotImplementedError, "parse_document_fragment"

class Store(AbstractStore, AbstractHandler):

    """
    A store class providing, in each instance, a wrapper around an underlying
    store, convenience attributes based on namespaces from the Format module and
    node types from the underlying store implementation, and a selection of
    higher-level operations relevant to parsing and writing.
    """

    prefix = None               # Defines the store's default namespace prefix.
    connector_labels = []       # Defines predicates which link to other nodes.
    uriref_labels = []          # Defines labels referring to URIRefs.

    def __init__(self, store, impl, prefix=None):

        """
        Initialise the store with the given underlying 'store' and
        implementation 'impl'. The additional 'prefix' specifies the namespace
        prefix which may qualify properties/predicates associated with this
        store.
        """

        self.store = store
        self.impl = impl

        # Override any class attributes.

        if prefix is not None:
            self.prefix = prefix

        # Copy in useful attributes.

        self.Literal = self.impl.Literal
        self.Namespace = self.impl.Namespace
        self.URIRef = self.impl.URIRef
        self.BNode = self.impl.BNode
        self.TYPE = self.Namespace(rdftype)

        # Set up the store's namespace prefix.

        if self.prefix is None:
            raise ValueError, "Please specify a prefix for this store."

        self.ns = self.Namespace(self.prefix)

    def get_context(self, context):

        """
        Return a copy of this store which uses the given 'context' to constrain
        operations on the stored triples.
        """

        return self.__class__(self.store.get_context(context), self.impl)

    def contexts(self):

        "Return a list of contexts found in this store."

        return self.store.contexts()

    def close(self):

        "Close the underlying store."

        self.store.close()

    def commit(self):

        "Commit changes to the underlying store if appropriate."

        if hasattr(self.store, "commit"):
            self.store.commit()

    def rollback(self):

        "Roll back changes to the underlying store if appropriate."

        if hasattr(self.store, "rollback"):
            self.store.rollback()

    def remove_context(self, context):

        """
        Removes the specified 'context' from the database.
        """

        self.store.remove_context(context)

    # Enhanced store methods.

    def has_item(self, uriref):
        return uriref is not None and self.store.has_triple((uriref, self.TYPE, None))

    # Calendar-specific methods.

    def add_node(self, label, uriref=None):

        """
        Add a node using the given 'label' to indicate its type and an optional
        'uriref' to provide an identity. Return the node identity.
        """

        if uriref is not None:
            node = uriref
        else:
            node = self.BNode()

        self.store.add((node, self.TYPE, self.ns[label]))
        return node

    def remove_node(self, node, deep=0):

        """
        Remove the given 'node' and its attributes from the store. If the
        optional 'deep' flag is set (as is not the default), remove all linked
        nodes recursively, stopping only at connector attributes which should
        mark the interfaces between items of different types.
        """

        for _node, link, attribute in self.store.triples((node, None, None)):
            self.store.remove((_node, link, attribute))

            # Literal nodes cannot lead to others.

            if not isinstance(attribute, self.Literal):

                # Do not follow connections to other items or resources.

                if self.get_label(link) not in self.connector_labels:

                    # Either remove recursively.

                    if deep:
                        self.remove_node(attribute, deep)

                    # Or just remove any subnodes.

                    else:
                        self.store.remove((attribute, None, None))

    def add_attribute(self, parent, label):

        """
        Add to the given 'parent' a special attribute node with the given
        'label'. Return the created node.
        """

        # Create the attribute.

        attribute = self.BNode()
        attribute_type = self.ns[label]
        self.store.add((attribute, self.TYPE, attribute_type))

        # Associate the attribute with the current parent.

        self.store.add((parent, self.ns[label], attribute))
        return attribute

    def add_value(self, attribute, label, value):

        """
        Add to the given 'attribute', described by the given 'label', the
        specified 'value'.
        """

        # Use URIRef for certain labels (from Format module information).

        if label in self.uriref_labels:
            obj = self.URIRef(value)
        else:
            obj = self.Literal(value)
        self.store.add((attribute, self.ns[label], obj))

    def add_name(self, node, name):
        self.store.add((node, self.ns["name"], self.Literal(name)))

    def add_contains(self, node, element):
        self.store.add((node, self.ns["contains"], element))

    # Notation and data conversions.

    def get_node_type(self, node):

        "Return the type of the given 'node'."

        for s, p, node_type in self.store.triples((node, self.TYPE, None)):
            return node_type

        # NOTE: Raise exception if no node type found?

        return None

    def get_label(self, node):

        "Return a label representing the given 'node'."

        if unicode(node).startswith(self.ns):
            return unicode(node)[len(unicode(self.ns)):]
        else:
            return None

    def get_uid(self, node):

        """
        Return the uid for the given 'node' (a store identifier). Unlike
        'make_uid', this method distinguishes between simple non-URI identifiers
        and URIs.
        """

        if unicode(node).startswith(self.ns):
            return unicode(node)[len(unicode(self.ns) + "uid#"):]
        else:
            return None

    def make_uid(self, value):

        "Return a store identifier for the given plain uid 'value'."

        # Test for URI-like identifiers.
        # NOTE: Should be improved to cover more than http:// URIs.

        if value.startswith("http://") or value.startswith("/"):
            return value
        else:
            return unicode(self.ns) + "uid#" + value

# Public functions.

def open(store_name, store_type, context=None, **kw):

    """
    Open the store with the given 'store_name' of the given 'store_type',
    providing an optional 'context' where supported. Return a tuple consisting
    of the store object and the implementation.
    """

    if store_type == "sqltriples":
        from sqltriples import TripleStore
        import sqltriples
        istore = sqltriples.open(store_name, **kw)
        if context is not None:
            istore = istore.get_context(sqltriples.URIRef(context))
        return istore, sqltriples
    else:
        raise NotSupportedError, store_type

# vim: tabstop=4 expandtab shiftwidth=4
