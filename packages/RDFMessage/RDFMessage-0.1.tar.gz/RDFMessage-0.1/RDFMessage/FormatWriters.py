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

from RDFMessage.Format import *
import RDFFormats.FormatWriters

class MessageWriter:

    "A message writer class."

    def __init__(self, f):

        """
        Initialise the writer with a stream 'f'.
        """

        self.f = f

    def start_element(self, label):
        pass

    def end_element(self, label):
        pass

    def write_attribute(self, name, modifiers=None, value=None, subvalues=None, multivalues=None):

        # NOTE: Modifiers, subvalues, multivalues not yet supported.

        if value is not None:
            self.f.write(name)
            self.f.write(": ")
            self.f.write(value + "\r\n")

    def close(self):
        self.f.close()

class DOMWriter(RDFFormats.FormatWriters.DOMWriter):

    "A DOM document writer."

    def get_item_type_name(self, label):
        # NOTE: Do this properly.
        return label

    def get_property_name(self, attribute_name):
        return attribute_name.lower()

    def get_property_label(self, property_name):
        return get_property_label(property_name)

# vim: tabstop=4 expandtab shiftwidth=4
