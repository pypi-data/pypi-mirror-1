#!/usr/bin/env python

"""
Conversion of messages to and from RDF representations.

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

--------

To parse mailboxes, use the parse_mailbox function provided in this module:

resource = RDFMessage.Parsers.parse_mailbox(f, store)

In the above call, f should be a stream providing message data, and store
should be some kind of object which can understand the actions of the parsing
process; in the RDFMessage.Store module, some classes are provided for this
activity.

To interpret the contents of DOM documents, use the parse_document and
parse_document_fragment functions provided in this module.
"""

from RDFMessage.Format import *
import email, mailbox, time

# Exceptions.

class DuplicateResourceError(Exception):
    pass

# Utility functions.

def check_existing(store, uriref):
    if uriref is not None and store.has_item(uriref):
        raise DuplicateResourceError, uriref

def find_uid(message):
    return message.get("Message-ID")

def add_message(store, attributes, node_type="e-mail", uriref=None):

    # Where appropriate, make a "uid".

    uid = find_uid(attributes)
    if uid is not None:
        uriref = store.URIRef(store.make_uid(uid))

    # Make the node.

    node = store.add_node(node_type, uriref)

    # Detect character encoding, if appropriate.

    if hasattr(attributes, "get_charset"):
        encoding = attributes.get_charset()
    else:
        encoding = None

    # Process the attributes.

    for header_name, value in attributes.items():
        attribute_name = attribute_names.get(header_name) or header_name.lower()
        attribute = store.add_attribute(node, attribute_name)
        label = get_property_label(attribute_name) or "details"
        if not isinstance(value, unicode):
            value = unicode(value, encoding or "iso-8859-1") # NOTE: Hack!
        if permitted_labels.get(attribute_name) == "datetime":
            value = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(time.mktime(email._parseaddr.parsedate(value))))
        store.add_value(attribute, label, value)

    return node

class MailboxParser:

    "A mailbox parser."

    def parse(self, f, store, uriref):

        """
        Parse the contents of the file object 'f', looking for message
        information to be recorded in the given 'store'. Use the given 'uriref'
        value to define a unique identifier for the parsed file.
        """

        # Check for existing entries.

        check_existing(store, uriref)
        mbox_node = store.add_node("mailbox", uriref=uriref)

        # Start parsing, employing the mailbox and email modules.

        mbox = mailbox.PortableUnixMailbox(f, factory=email.message_from_file)
        for message in mbox:
            node = add_message(store, message)
            store.add_contains(mbox_node, node)

        return mbox_node

class DOMParser:

    "A parser which reads messages from DOM documents."

    def parse(self, doc, root, store, uriref):

        """
        Parse the contents of the given document 'doc', looking for resource
        information at and below the 'root' element. Insert information into the
        given 'store', associated with the given 'uriref'.
        """

        # Check for existing entries.

        check_existing(store, uriref)

        attributes = {}
        for element in root.xpath("*"):

            # Check the element name against the list of known headers.

            name = element.localName
            if property_names.has_key(name):
                value = self.find_attribute_value(element)
                attributes[name] = value

        # Store the message.

        node = add_message(store, attributes, uriref=uriref)
        return node

    def find_attribute_value(self, element):

        attribute_name = element.localName
        default_label_name = get_property_label(attribute_name) or "details"

        for attr in element.xpath("@*"):
            label_name = attr.localName
            if not label_name == (default_label_name):
                continue
            return attr.nodeValue

        # Check also for child text nodes.

        text_nodes = element.xpath("./text()")
        if text_nodes:
            return "".join([n.nodeValue for n in text_nodes])

        return None

# Public functions.

def parse_mailbox(f, store, uriref):

    """
    Parse the message data found through the use of the file object 'f', and
    put the resource information in the given 'store'.

    The 'uriref' parameter must be used to set a unique reference to the
    resource by defining a specific URI reference.

    As a result of parsing the resource, the root node of the imported resource
    is returned.
    """

    parser = MailboxParser()
    return parser.parse(f, store, uriref=uriref)

def parse_document(doc, store, uriref=None):

    """
    Parse the resource data found in the given DOM document 'doc', inserting the
    information in the given 'store'. The 'uriref' must be specified to define
    the identity of the root node.
    """

    parser = DOMParser()
    return parser.parse(doc, doc.xpath("*")[0], store, uriref=uriref)

def parse_document_fragment(doc, root, store, uriref=None):

    """
    Parse the resource data found in the given DOM document 'doc' under the
    'root' element, inserting the information in the given 'store'. The
    'uriref' must be specified to define the identity of the root node.
    """

    parser = DOMParser()
    return parser.parse(doc, root, store, uriref=uriref)

# vim: tabstop=4 expandtab shiftwidth=4
