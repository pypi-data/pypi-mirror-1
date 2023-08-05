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

from RDFMessage.Format import *
import RDFMessage.FormatWriters
import RDFFormats.Writers
import libxml2dom

# Serialisation.

class Writer(RDFFormats.Writers.Writer):

    def write_uid(self, uid):
        pass

        #self.format_writer.write_attribute("Message-ID", value=uid)

    def write_attribute(self, store, attribute_name, attribute):

        """
        Write the attribute found in the 'store' with the given 'attribute_name'
        and represented by 'attribute'. This method invokes the format writer's
        'write_attribute' method.
        """

        if isinstance(attribute, store.Literal):
            self.format_writer.write_attribute(attribute_name, value=unicode(attribute))

        else:

            # Find out which object is the value.

            property_name = attribute_name.lower()
            value_label = get_property_label(property_name) or "details"

            # Find and write values.

            for subject, predicate, value in store.store.triples((attribute, store.ns[value_label], None)):
                self.format_writer.write_attribute(attribute_name, value=unicode(value))
                break

    def is_element_permitted(self, subelement_name, element_name):
        return 0 # NOTE: Should probably include attachments.

    def is_attribute_permitted(self, attribute_name, element_name):
        return 1 # NOTE: Should probably test more strictly.

def _make_document(label):

    "Make a document with the given 'label' and return it."

    doc = libxml2dom.createDocument(unicode(rdfmessage), "message:%s" % label, None)
    return doc

def _write_nodes(writer, store, main_node, nodes):

    """
    Write, using the given 'writer' and the given 'store', either the given
    'main_node' or the given 'nodes'.
    """

    if main_node is not None:
        writer.write(store, main_node)
    elif nodes is not None:
        for node in nodes:
            writer.write(store, node)

# Public functions.

def get_document(store, main_node=None, qualifier=None, value_as_attribute=0):

    """
    Using the given 'store', return a new DOM document containing the resource
    rooted at the given 'main_node', configured using the optional 'qualifier'
    and 'value_as_attribute' parameters.
    """

    node_type = store.get_node_type(main_node)
    if node_type is None:
        raise ValueError, main_node

    doc = _make_document(store.get_label(node_type))
    doc.removeChild(doc.childNodes[-1])
    write_to_document(doc, doc, store, main_node=main_node, qualifier=qualifier or (rdfmessage, "message:"), value_as_attribute=value_as_attribute)
    return doc

def get_document_for_nodes(store, label, nodes, qualifier=None, value_as_attribute=0):

    """
    Using the given 'store', make a new DOM document with the given 'label' on
    the root element containing the resources found at the given 'nodes',
    configured using the optional 'qualifier' and 'value_as_attribute'
    parameters.
    """

    doc = _make_document(label)
    write_to_document(doc, doc.childNodes[-1], store, nodes=nodes,
        qualifier=qualifier or (rdfmessage, "message:"), value_as_attribute=value_as_attribute)
    return doc

def write_to_stream(stream, store, main_node=None, nodes=None, *args, **kw):

    """
    Write to the given 'stream', using the given 'store', the 'main_node' (if
    specified) or the given 'nodes' (if specified instead).
    """

    writer = Writer(RDFMessage.FormatWriters.MessageWriter(stream, *args, **kw))
    _write_nodes(writer, store, main_node, nodes)

def write_to_document(doc, root, store, main_node=None, nodes=None, qualifier=None, value_as_attribute=0):

    """
    Write to the document 'doc' within the given 'root' element, using the given
    'store', the 'main_node' (if specified) or the given 'nodes' (if specified
    instead). The optional 'qualifier' and 'value_as_attribute' settings
    configure the resulting DOM document.
    """

    writer = Writer(RDFMessage.FormatWriters.DOMWriter(doc, root, qualifier=qualifier or (rdfmessage, "message:"), value_as_attribute=value_as_attribute))
    _write_nodes(writer, store, main_node, nodes)

# vim: tabstop=4 expandtab shiftwidth=4
