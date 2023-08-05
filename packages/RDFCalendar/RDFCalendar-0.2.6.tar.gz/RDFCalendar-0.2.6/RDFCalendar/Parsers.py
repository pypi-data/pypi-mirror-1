#!/usr/bin/env python

"""
Conversion of iCalendar files to and from RDF representations.

Copyright (C) 2005, 2006, 2007 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

--------

Note on relationships/predicates between nodes/references:

    * The "contains" relationship is used between elements.
    * Predicates from elements to attributes typically bear the type of the
      attributes.
    * Multivalues are represented by numerous "value" nodes, each linked to
      nodes via relationships bearing specific labels.

To parse iCalendar files, use the parse function provided in this module:

resource = RDFCalendar.Parsers.parse(f, store)

In the above call, f should be a stream providing iCalendar data, and store
should be some kind of object which can understand the actions of the parsing
process; in the RDFCalendar.Store module, some classes are provided for this
activity. For the storage of iCalendar data, objects instantiated from the Store
class can be supplied to the parse function; for interpreting free/busy requests,
objects instantiated from the FreeBusyRequest class can be supplied.

To interpret the contents of DOM documents, use the parse_document and
parse_document_fragment functions provided in this module.
"""

from RDFCalendar.Format import *

# Encoding-related imports.

import base64, quopri

# Exceptions.

class DuplicateResourceError(Exception):
    pass

# Utility functions.

def check_existing(store, uriref):
    if uriref is not None and store.has_item(uriref):
        raise DuplicateResourceError, uriref

def find_uid(attributes):

    """
    Find the unique identifier in 'attributes', returning such an identifier
    (or None if no such identifier was found). The 'attributes' are modified
    if an identifier was found, with the attribute providing the identifier
    removed.
    """

    i = 0
    for i in range(0, len(attributes)):
        attribute_name, modifiers, values = attributes[i]
        if attribute_name == "UID":
            uid = values[0][1]
            del attributes[i]
            return uid
    return None

def add_node(store, attributes, node_type, uriref=None):

    """
    Add a node described by the given 'attributes' and 'node_type' to the
    store. The 'attributes' parameter is a list of items of the following
    form: (name-string, modifiers-dictionary, value-tuple-list). The latter
    value-tuple-list consists of items of the following form: (qualifier,
    value-string).

    If the optional 'uriref' is specified, override any unique identifier
    found in the 'attributes'.
    """

    # Where appropriate, make a "uid".

    uid = find_uid(attributes)
    if uriref is None:
        if uid is not None:
            uriref = store.URIRef(store.make_uid(uid))

    # Make the node.

    node = store.add_node(node_type, uriref)

    # Process the attributes.

    for attribute_name, modifiers, values in attributes:

        # If the attribute refers to another, do not create a special attribute
        # node.

        if attribute_name in connector_attributes:
            if len(values) == 1:

                # Ignore empty values.

                if values[0][1]:
                    store.add_value(node, attribute_name.lower(), store.make_uid(values[0][1]))
            #else:
            #    raise ValueError, (attribute_name, values)
            continue

        # First add the attribute.

        property_name = attribute_name.lower()
        attribute = store.add_attribute(node, property_name)

        # Add the modifiers to the new node.

        for modifier_name, modifier_value in modifiers.items():
            store.add_value(attribute, modifier_name.lower(), modifier_value)

        # Add the values to the new node.

        for label, value in values:

            # If the value is a complicated type, add subvalues.

            if label is None:
                subattribute = store.add_attribute(attribute, "value")
                for sublabel, subvalue in value:
                    store.add_value(subattribute, sublabel, subvalue)
            else:
                label = get_property_label(property_name) or label.lower()
                store.add_value(attribute, label, value)

    return node

# Simple reader class.

class Reader:

    "A simple class wrapping a file, providing simple pushback capabilities."

    def __init__(self, f, non_standard_newline=0):

        """
        Initialise the object with the file 'f'. If 'non_standard_newline' is
        set to a true value (unlike the default), lines ending with CR will be
        treated as complete lines.
        """

        self.f = f
        self.non_standard_newline = non_standard_newline
        self.lines = []
        self.line_number = 0

    def pushback(self, line):

        """
        Push the given 'line' back so that the next line read is actually the
        given 'line' and not the next line from the underlying file.
        """

        self.lines.append(line)
        self.line_number -= 1

    def readline(self):

        """
        If no pushed-back lines exist, read a line directly from the file.
        Otherwise, read from the list of pushed-back lines.
        """

        self.line_number += 1
        if self.lines:
            return self.lines.pop()
        else:
            # NOTE: Sanity check for broken lines (\r instead of \r\n or \n).
            line = self.f.readline()
            while line.endswith("\r") and not self.non_standard_newline:
                line += self.f.readline()
            if line.endswith("\r") and self.non_standard_newline:
                return line + "\n"
            else:
                return line

    def read_until(self, targets):

        """
        Read from the stream until one of the 'targets' is seen. Return the
        string from the current position up to the target found, along with the
        target string, using a tuple of the form (string, target). If no target
        was found, return the entire string together with a target of None.
        """

        indexes = {}

        # Remember the entire text read and the index of the current line in
        # that text.

        lines = []

        line = self.readline()
        lines.append(line)
        start = 0

        while indexes == {} and line != "":
            for target in targets:
                index = line.find(target)

                # Always choose the first matching target.

                if index != -1 and not indexes.has_key(start + index):
                    indexes[start + index] = target

            start += len(line)
            line = self.readline()
            lines.append(line)

        text = "".join(lines)

        if indexes != {}:
            min_index = reduce(min, indexes.keys())
            target = indexes[min_index]

            # Skip the target.
            # Since the end of the buffer should always be a newline, ignore the
            # last element.

            lines = text[min_index + len(target):].split("\n")[:]
            if not lines[-1]:
                del lines[-1]
            lines.reverse()

            for line in lines:
                self.pushback(line + "\n")

            return text[:min_index], target
        else:
            return text, None

class iCalendarParser:

    "An iCalendar parser."

    def parse(self, f, store, name=None, uriref=None):

        """
        Parse the contents of the file 'f', looking for calendar information to be
        recorded in the given 'store'. If the optional 'name' is specified, tag the
        calendar with that information. If the optional 'uriref' is supplied, use the
        value to override any unique identifier provided in the parsed file.
        """

        # Check for existing entries.

        check_existing(store, uriref)

        # Start parsing, looking for an opening declaration.

        keyword, modifiers, values = self.parse_attribute_text(f)
        while not (keyword == "BEGIN" and (
            ("details", "VCALENDAR") in values or
            ("details", "VCARD") in values)):

            keyword, modifiers, values = self.parse_attribute_text(f)

        # Assume we now have a calendar. If none was present, the end of the file
        # would have been reached and an exception raised.

        calendar = None
        while keyword == "BEGIN":

            if ("details", "VCALENDAR") in values:
                calendar = self.parse_element(f, store, "VCALENDAR", calendar, uriref=uriref)
            elif ("details", "VCARD") in values:
                calendar = self.parse_element(f, store, "VCARD", calendar, uriref=uriref)
            else:
                break

            # NOTE: Nasty means of ending.

            try:
                keyword, modifiers, values = self.parse_attribute_text(f)
            except ValueError:
                break

        if name is not None:
            store.add_name(calendar, name)

        return calendar

    def parse_element(self, f, store, label, existing_node=None, uriref=None):

        """
        Parse the object being read from the file 'f', recording the details in
        the given 'store'. The 'label' is used to recognise the end of the object
        definition. If an 'existing_node' is supplied, no new node is created for
        the element, but dependent elements are added to the given 'existing_node'.
        If an 'uriref' is supplied, use the value to override any unique identifier
        provided in the parsed file.
        The last line read from the file should have been the start of the object
        definition.
        """

        attributes = []
        elements = []

        # Read lines until the end of the element is found.

        keyword, modifiers, values = self.parse_attribute_text(f)
        while not (keyword == "END" and ("details", label) in values):

            # If an element is found, parse it and record its details in the store.

            if keyword == "BEGIN":
                element_name = self.get_details(values)
                if element_name in permitted_elements[label]:
                    elements.append(self.parse_element(f, store, element_name))
                else:
                    raise ValueError, (element_name, f.line_number)

            # If an attribute is found, parse it and record the details for later
            # storage.

            else:
                attribute_name = keyword
                if attribute_name in permitted_attributes[label]:
                    attributes.append((attribute_name, modifiers, values))
                else:
                    #raise ValueError, (attribute_name, f.line_number)
                    pass

            keyword, modifiers, values = self.parse_attribute_text(f)

        # Associate the element with its attributes.

        if existing_node is None:
            node = add_node(store, attributes, element_names[label], uriref=uriref)
        else:
            node = existing_node

        # Associate all elements found within this element to the element itself.

        for element in elements:
            store.add_contains(node, element)

        return node

    def parse_attribute_text(self, f):

        """
        Using the file 'f', return the attribute name, attribute
        modifiers/properties, and a list containing value information for the
        attribute information in the file.
        """

        modifiers = {}
        attribute_name, sep = f.read_until([";", ":"])
        attribute_name = attribute_name.strip()

        while sep == ";":

            # Find the actual modifier.

            modifier_name, sep = f.read_until(["=", ";", ":"])
            modifier_name = modifier_name.strip()

            if sep == "=":
                modifier_value, sep = f.read_until([";", ":"])
                modifier_value = modifier_value.strip()
            else:
                modifier_value = None

            # Append a key, value tuple to the modifiers list.

            modifiers[modifier_name] = modifier_value

        # Get the value content.

        if sep != ":":
            raise ValueError, f.line_number

        # Strip all appropriate whitespace from the right end of each line.
        # For subsequent lines, remove the first whitespace character.
        # NOTE: The iCalendar specification has some rules about whitespace that
        # NOTE: should be applied here.

        line = f.readline()
        value_lines = [line.rstrip("\r\n")]
        line = f.readline()
        while line != "" and line[0] in [" ", "\t"]:
            value_lines.append(line.rstrip("\r\n")[1:])
            line = f.readline()

        # Since one line too many will have been read, push the line back into the
        # file.

        f.pushback(line)

        # Handle the content in different ways, according to the attribute name.
        # NOTE: The presence of non-quoted characters might be a better
        # NOTE: indicator of which kind of content is being processed.

        if attribute_name in subvalue_attributes:

            # Find the set of values.
            # NOTE: No additional spaces reintroduced.

            value_string = self.decode("".join(value_lines), modifiers.get("ENCODING"))
            value_pairs = value_string.split(";")
            values = []
            for value_pair in value_pairs:
                value_tuple = value_pair.split("=")
                value = value_tuple[0], "=".join(value_tuple[1:])
                values.append(value)

        elif attribute_name in multivalue_attributes + period_attributes:

            # Find the set of values.
            # NOTE: This may jumble the datetimes up if they overlap.

            value_string = self.decode("".join(value_lines), modifiers.get("ENCODING"))

            values = []
            for value_string_element in value_string.split(","):
                value_list = value_string_element.split("/")

                # For period attributes.

                if len(value_list) == 2:
                    value = [("start", value_list[0])]

                    # NOTE: Consider calculating the end for durations.

                    if value_list[1][0] in "+-P":
                        value.append(("duration", value_list[1]))
                    else:
                        value.append(("end", value_list[1]))

                # For multivalue attributes.

                elif len(value_list) == 1:
                    value.append(("details", value_string_element))

                # Here, None means "containing subvalues".

                values.append((None, value))

        else:

            # Get the entire value string.

            value = self.decode("".join(value_lines), modifiers.get("ENCODING"))
            values = [("details", value)]

        # Remove the encoding modifier.

        if modifiers.has_key("ENCODING"):
            del modifiers["ENCODING"]
        return attribute_name, modifiers, values

    def decode(self, value, encoding):

        "Decode the 'value' with the given 'encoding'."

        # NOTE: Assuming ISO 8869-1 for the character set.

        if encoding == "QUOTED-PRINTABLE":
            return unicode(quopri.decodestring(value), "iso-8859-1")
        elif encoding == "BASE64":
            return base64.decodestring(value)
        else:
            # NOTE: Introducing newline conversions.
            # Replace quoted characters (see 4.3.11 in RFC 2445).

            return value.replace("\r", "").replace("\\N", "\n").replace("\\n", "\n").replace("\\,", ",").replace("\\;", ";")

    def get_details(self, values):
        for key, value in values:
            if key == "details":
                return value
        return None

class DOMParser:

    "A parser which reads resource definitions from DOM documents."

    def parse(self, doc, root, store, uriref=None):

        """
        Parse the contents of the given document 'doc', looking for resource
        information at and below the 'root' element. Insert information into the
        given 'store'.
        """

        # Check for existing entries.

        check_existing(store, uriref)
        self.parse_element(root, store, uriref=uriref)

    def parse_element(self, element, store, uriref=None):

        """
        Parse the given 'element', inserting information found within it into
        the given 'store'.
        """

        attributes = []
        elements = []

        # Check the element name against the list of permitted element names.

        item_type_name = element.localName
        if not item_type_names.has_key(item_type_name):
            raise ValueError, item_type_name

        # Remember the property name, derived from the element name.

        property_name = item_type_names[item_type_name]

        for subelement in element.xpath("*"):

            # Check the element name against the list of permitted attribute and
            # element names.
            # NOTE: We could exclude xmlns attributes in many places, but the
            # NOTE: permitted attributes dictionary should catch and reject such
            # NOTE: attributes.

            name = subelement.localName
            subproperty_name = item_type_names.get(name)
            attribute_name = name.upper()

            if subproperty_name in permitted_elements[property_name]:
                elements.append(self.parse_element(subelement, store))

            elif attribute_name in permitted_attributes[property_name]:
                values = self.parse_attribute_values(subelement)

                # NOTE: No modifiers in use here.

                attributes.append((attribute_name, {}, values))

        # Store the element.

        node = add_node(store, attributes, item_type_name, uriref=uriref)

        # Associate all elements found within this element to the element itself.

        for element in elements:
            store.add_contains(node, element)

        return node

    def parse_attribute_values(self, element):

        # Check each attribute name against the list of permitted label
        # names.

        property_name = element.localName
        attribute_name = property_name.upper()
        default_label_name = get_property_label(property_name) or "details"

        values = []
        for attr in element.xpath("@*"):
            label_name = attr.localName
            if not label_name == (default_label_name):
                continue
            values.append((label_name, attr.nodeValue))

        # Check also for child text nodes.

        text_nodes = element.xpath("./text()")
        if text_nodes:
            values.append((default_label_name, "".join([n.nodeValue for n in text_nodes])))

        return values

# Public functions.

def parse(f, store, name=None, uriref=None, non_standard_newline=0):

    """
    Parse the resource data found through the use of the file object 'f', which
    should provide Unicode data, and put the resource information in the given
    'store'. (The codecs module can be used to open files or to wrap streams in
    order to provide Unicode data.)

    The optional 'name' and 'uriref' parameters can be used to respectively set
    the name of the imported resource and to override the unique identifier of
    the resource with a specific URI reference.

    The optional 'non_standard_newline' can be set to a true value (unlike the
    default) in order to attempt to process files with CR as the end of line
    character.

    As a result of parsing the resource, the root node of the imported resource
    is returned.
    """

    reader = Reader(f, non_standard_newline=non_standard_newline)
    parser = iCalendarParser()
    return parser.parse(reader, store, name=name, uriref=uriref)

def parse_document(doc, store, uriref=None):

    """
    Parse the resource data found in the given DOM document 'doc', inserting the
    information in the given 'store'. If the optional 'uriref' is specified,
    override any unique identifier information in choosing the identity of the
    root node.
    """

    parser = DOMParser()
    return parser.parse(doc, doc.xpath("*")[0], store, uriref=uriref)

def parse_document_fragment(doc, root, store, uriref=None):

    """
    Parse the resource data found in the given DOM document 'doc' under the
    'root' element, inserting the information in the given 'store'. If the
    optional 'uriref' is specified, override any unique identifier information
    in choosing the identity of the root node.
    """

    parser = DOMParser()
    return parser.parse(doc, root, store, uriref=uriref)

# vim: tabstop=4 expandtab shiftwidth=4
