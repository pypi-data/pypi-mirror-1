#!/usr/bin/env python

"""
Storage of nodes according to RDFMessage conventions.

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

import RDFFormats.Store
from RDFMessage.Format import *
import RDFMessage.Writers
import RDFMessage.Parsers

class Store(RDFFormats.Store.Store):

    "A store providing support for the parsing and writing of messages."

    prefix = rdfmessage
    connector_labels = connector_labels
    uriref_labels = uriref_labels

    # Special FormatWriter methods.

    def get_element_name(self, predicate):

        "Return the element name for the given store 'predicate' identifier."

        # NOTE: Add some kind of element name support later.
        return self.get_label(predicate)

    def get_attribute_name(self, predicate):

        "Return the attribute name for the given store 'predicate' identifier."

        label = self.get_label(predicate)
        if label is not None:
            return property_names.get(label) or label
        else:
            return None

    # WebOrganiser handler methods.

    def get_urirefs_for_item_type(self, item_type_name):
        if item_type_name in supported_item_types:
            return [self.ns[item_type_name]]
        else:
            return []

    def get_urirefs_for_property_type(self, property_type_name):
        if property_type_name in all_labels:
            return [self.ns[property_type_name]]
        elif property_type_name == "summary":
            return [self.ns["subject"]]
        elif property_type_name == "created":
            return [self.ns["date"]]
        else:
            return []

    def get_property_types_for_uriref(self, uriref):
        label = self.get_label(uriref)
        if label == "subject":
            return ["summary"]
        elif label == "date":
            return ["created"]
        else:
            return []

    def get_urirefs_for_attribute(self, attribute):
        if attribute == "person":
            return [
                [self.ns["from"], self.ns["uri"]],
                [self.ns["to"], self.ns["uri"]]
                ]
        elif attribute == "related-to":
            return [
                [self.ns["related-to"]]
                ]
        else:
            return []

    def supports_item_type(self, item_type_str):
        return item_type_str in supported_item_types

    def get_supported_item_types(self):
        return supported_item_types

    def write_to_stream(self, stream, main_node=None, nodes=None, *args, **kw):
        RDFMessage.Writers.write_to_stream(stream, self, main_node, nodes, *args, **kw)

    def write_to_document(self, doc, root, main_node=None, nodes=None, qualifier=None, value_as_attribute=0):
        RDFMessage.Writers.write_to_document(doc, root, self, main_node, nodes, qualifier, value_as_attribute)

    def parse(self, f, uriref=None):
        return RDFMessage.Parsers.parse(f, self, uriref)

    def parse_document_fragment(self, doc, root, uriref=None):
        return RDFMessage.Parsers.parse_document_fragment(doc, root, self, uriref)

    # WebOrganiser exposed exceptions.

    DuplicateResourceError = RDFMessage.Parsers.DuplicateResourceError

# Public functions.

def open(store_name, store_type, context=None, **kw):

    """
    Open the store with the given 'store_name' of the given 'store_type',
    providing an optional 'context' where supported.
    """

    return Store(*RDFFormats.Store.open(store_name, store_type, context, **kw))

# vim: tabstop=4 expandtab shiftwidth=4
