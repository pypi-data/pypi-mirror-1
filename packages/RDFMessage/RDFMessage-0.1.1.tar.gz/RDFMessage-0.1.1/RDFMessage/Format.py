#!/usr/bin/env python

"""
Constants for parsing and writing.

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

# Plain rdfmessage and other namespaces.

rdfmessage = "http://www.boddie.org.uk/ns/rdfmessage/"
rdftype = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

# Supported headers.

attribute_names = {
    "From" : "from",
    "To" : "to",
    "Cc" : "cc",
    "Subject" : "subject",
    "Message-ID" : "message-id",
    "In-Reply-To" : "in-reply-to",
    "References" : "references",
    "Date" : "date"
    }

property_names = {}
for key, value in attribute_names.items():
    property_names[value] = key

# Attribute/header labels.

permitted_labels = {
    "from" : "uri",
    "to" : "uri",
    "cc" : "uri",
    "date" : "datetime"
    }

# Label types.

connector_labels = ["related-to", "from", "to", "cc"]
uriref_labels = ["uri", "related-to"]
all_labels = ["uri", "related-to", "details", "datetime"]

# Supported item types.

supported_item_types = ["e-mail"]

# Format helper functions.

def get_property_label(property_name):

    """
    Return the special property label for the given 'property_name', or None
    if a generic label is to be used (for example, to construct a predicate for
    RDF triple stores).
    """

    return permitted_labels.get(property_name)

# vim: tabstop=4 expandtab shiftwidth=4
