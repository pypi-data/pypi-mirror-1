#!/usr/bin/env python

"""
Storage of nodes according to RDFCalendar conventions.

Copyright (C) 2005, 2006, 2007 Paul Boddie <paul@boddie.org.uk>

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
from RDFCalendar.Format import *
import RDFCalendar.Writers
import RDFCalendar.Parsers

class Store(RDFFormats.Store.Store):

    """
    A wrapper around a data store, providing convenient access for parsers and
    writers.
    """

    prefix = rdfcalendar
    connector_labels = connector_labels
    uriref_labels = uriref_labels

    # Special FormatWriter methods.

    def get_element_name(self, predicate):

        "Return the element name for the given store 'predicate' identifier."

        return item_type_names[self.get_label(predicate)]

    def get_attribute_name(self, predicate):

        "Return the attribute name for the given store 'predicate' identifier."

        label = self.get_label(predicate)
        if label is not None:
            return label.upper()
        else:
            return None

    # WebOrganiser handler methods.

    def get_urirefs_for_item_type(self, item_type_name):
        if item_type_names.has_key(item_type_name):
            return [self.ns[item_type_name]]
        else:
            return []

    def get_urirefs_for_property_type(self, property_type_name):
        if property_type_name in all_labels + value_labels:
            return [self.ns[property_type_name]]
        else:
            return []

    def get_property_types_for_uriref(self, uriref):
        label = self.get_label(uriref)
        if label:
            return [label] # NOTE: URIs correspond to their labels for now.
        else:
            return []

    def get_urirefs_for_attribute(self, attribute):
        if attribute == "person":
            return [
                [self.ns["organizer"], self.ns["uri"]],
                [self.ns["attendee"], self.ns["uri"]]
                ]
        elif attribute == "person-name":
            return [
                [self.ns["fn"], self.ns["details"]],
                [self.ns["e-mail"], self.ns["details"]]
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
        RDFCalendar.Writers.write_to_stream(stream, self, main_node, nodes, *args, **kw)

    def write_to_document(self, doc, root, main_node=None, nodes=None, qualifier=None, value_as_attribute=0):
        RDFCalendar.Writers.write_to_document(doc, root, self, main_node, nodes, qualifier, value_as_attribute)

    def parse(self, f, name=None, uriref=None, non_standard_newline=0):
        return RDFCalendar.Parsers.parse(f, self, name, uriref, non_standard_newline=non_standard_newline)

    def parse_document_fragment(self, doc, root, uriref=None):
        return RDFCalendar.Parsers.parse_document_fragment(doc, root, self, uriref)

    # WebOrganiser exposed exceptions.

    DuplicateResourceError = RDFCalendar.Parsers.DuplicateResourceError

# Special non-typical store-like classes.

class FreeBusyRequest(RDFFormats.Store.AbstractStore):

    "A record of free/busy request information."

    def __init__(self):
        self.start = None
        self.end = None
        self.organiser = None
        self.attendee = None
        self.nodes = []

    def has_item(self, uriref):
        return 0

    def add_node(self, attributes, label, uriref=None):
        for attribute_name, modifiers, values in attributes:
            if attribute_name == "DTSTART":
                self.start = values[0][1]
            elif attribute_name == "DTEND":
                self.end = values[0][1]
            elif attribute_name == "ORGANIZER":
                self.organiser = values[0][1]
            elif attribute_name == "ATTENDEE":
                self.attendee = values[0][1]
        self.nodes.append((attributes, label, uriref))
        return str(len(self.nodes) - 1)

    def add_name(self, node, name):
        pass

    def add_contains(self, node, element):
        pass

class DebugStore(RDFFormats.Store.AbstractStore):

    "A class displaying store operations."

    def __init__(self):
        self.n = 0

    def has_item(self, uriref):
        print "has_item(%r)" % uriref
        return 0

    def add_node(self, attributes, label, uriref=None):
        print "add_node(%r, %r, %r)" % (attributes, label, uriref)
        self.n += 1
        return str(self.n)

    def add_name(self, node, name):
        print "add_name(%r, %r)" % (node, name)

    def add_contains(self, node, element):
        print "add_contains(%r, %r)" % (node, element)

    def add_attribute(self, parent, label):
        print "add_attribute(%r, %r)" % (parent, label)
        self.n += 1
        return str(self.n)

    def add_value(self, attribute, label, value):
        print "add_value(%r, %r, %r)" % (attribute, label, value)

# Public functions.

def open(store_name, store_type, context=None, **kw):

    """
    Open the store with the given 'store_name' of the given 'store_type',
    providing an optional 'context' where supported.
    """

    return Store(*RDFFormats.Store.open(store_name, store_type, context, **kw))

# vim: tabstop=4 expandtab shiftwidth=4
