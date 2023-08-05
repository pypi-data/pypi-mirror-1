#!/usr/bin/env python

"""
Writer classes.

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
"""

from RDFCalendar.Format import *
import RDFCalendar.FormatWriters
import RDFFormats.Writers
import libxml2dom

# Serialisation.

class Writer(RDFFormats.Writers.Writer):

    def write_uid(self, uid):
        self.format_writer.write_attribute("UID", value=uid)

    def write_attribute(self, store, attribute_name, attribute):

        """
        Write the attribute found in the 'store' with the given 'attribute_name'
        and represented by 'attribute'. This method invokes the format writer's
        'write_attribute' method.
        """

        if isinstance(attribute, store.Literal):
            self.format_writer.write_attribute(attribute_name, value=unicode(attribute))

        elif attribute_name in subvalue_attributes:

            # All related nodes are subvalues.

            subvalues = []
            for subject, predicate, object in store.store.triples((attribute, None, None)):
                if predicate != store.TYPE:
                    subvalues.append((store.get_attribute_name(predicate), unicode(object)))

            self.format_writer.write_attribute(attribute_name, subvalues=subvalues)

        elif attribute_name in multivalue_attributes + period_attributes:

            # All related nodes are multivalues.

            multivalues = []
            for subject, predicate, value in store.store.triples((attribute, None, None)):
                if predicate != store.TYPE:
                    multivalue = {}
                    for _value, _predicate, object in store.store.triples((value, None, None)):
                        if _predicate != store.TYPE:
                            multivalue[store.get_attribute_name(_predicate)] = unicode(object)
                    multivalues.append(multivalue)

            self.format_writer.write_attribute(attribute_name, multivalues=multivalues)

        elif attribute_name in connector_attributes:

            # If the attribute refers to another, use the UID of that node.

            uid_or_uriref = store.get_uid(attribute) or attribute
            self.format_writer.write_attribute(attribute_name, value=uid_or_uriref)

        else:

            # Find out which object is the value.

            property_name = attribute_name.lower()
            value_label = get_property_label(property_name) or "details"

            # Find modifiers.

            modifiers = []
            for subject, predicate, object in store.store.triples((attribute, None, None)):
                if predicate == store.ns[value_label]:
                    pass
                elif predicate != store.TYPE:
                    modifiers.append((store.get_attribute_name(predicate), unicode(object)))

            # Find and write values.

            for subject, predicate, value in store.store.triples((attribute, store.ns[value_label], None)):
                self.format_writer.write_attribute(attribute_name, modifiers=modifiers, value=unicode(value))
                break

    def is_element_permitted(self, subelement_name, element_name):
        return subelement_name in permitted_elements[element_name]

    def is_attribute_permitted(self, attribute_name, element_name):
        return attribute_name in permitted_attributes[element_name]

def _make_document(label):

    "Make a document with the given 'label' and return it."

    doc = libxml2dom.createDocument(rdfcalendar, "calendar:%s" % label, None)
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
    write_to_document(doc, doc, store, main_node=main_node, qualifier=qualifier or (rdfcalendar, "calendar:"), value_as_attribute=value_as_attribute)
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
        qualifier=qualifier or (rdfcalendar, "calendar:"), value_as_attribute=value_as_attribute)
    return doc

def write_to_stream(stream, store, main_node=None, nodes=None, *args, **kw):

    """
    Write to the given 'stream', using the given 'store', the 'main_node' (if
    specified) or the given 'nodes' (if specified instead).
    """

    writer = Writer(RDFCalendar.FormatWriters.iCalendarWriter(stream, *args, **kw))
    _write_nodes(writer, store, main_node, nodes)

def write_to_document(doc, root, store, main_node=None, nodes=None, qualifier=None, value_as_attribute=0):

    """
    Write to the document 'doc' within the given 'root' element, using the given
    'store', the 'main_node' (if specified) or the given 'nodes' (if specified
    instead). The optional 'qualifier' and 'value_as_attribute' settings
    configure the resulting DOM document.
    """

    writer = Writer(RDFCalendar.FormatWriters.DOMWriter(doc, root, qualifier=qualifier or (rdfcalendar, "calendar:"), value_as_attribute=value_as_attribute))
    _write_nodes(writer, store, main_node, nodes)

def write_freebusy(stream, store, start, end, organiser, attendee, attendee_as_organiser=0, *args, **kw):

    """
    Write to the given 'stream', using the given 'store', the free/busy
    information in the time period from 'start' to 'end' (where None indicates
    the absence of a constraint on the period), in response to the 'organiser',
    for the person specified as the 'attendee'.

    If the optional 'attendee_as_organiser' parameter is set to a true value
    (which is not the default), items where the specified 'attendee' is also the
    organiser of an event are included in the free/busy information.
    """

    sqlstore = store.store
    writer = RDFCalendar.FormatWriters.iCalendarWriter(stream, *args, **kw)
    limit = None

    # Write the header.

    writer.start_element("VCALENDAR")
    writer.write_attribute("PRODID", value="-//RDFCalendar//NONSGML write_freebusy//EN")
    writer.write_attribute("VERSION", value=RDFCalendar.__version__)
    writer.write_attribute("METHOD", value="PUBLISH")
    writer.start_element("VFREEBUSY")
    writer.write_attribute("ORGANIZER", value=organiser)
    writer.write_attribute("ATTENDEE", value=attendee)

    # Write period information.

    if start:
        writer.write_attribute("DTSTART", value=start)
        if end:
            limit = sqlstore.Expression("_ >= ? and _ < ?", [start, end])
        else:
            limit = sqlstore.Expression("_ >= ?", [start])

    if end:
        writer.write_attribute("DTEND", value=end)
        if not start:
            limit = sqlstore.Expression("_ < ?", [end])

    # Find the attendee and all items where they have that role. If appropriate,
    # find all items where they also are the organiser of an event.

    resource = sqlstore.triples((None, store.ns["uri"], store.URIRef(attendee)))
    resource_attendee = sqlstore.triples((None, store.ns["attendee"], resource))
    if attendee_as_organiser:
        resource_organiser = sqlstore.triples((None, store.ns["organizer"], resource))
        resource_involved = sqlstore.or_subjects([resource_organiser, resource_attendee])
    else:
        resource_involved = resource_attendee

    # Exclude free/busy resources.

    not_freebusy = sqlstore.triples((resource_involved, store.TYPE, sqlstore.Expression("_ <> ?", [store.ns["free-busy"]], "U")))

    # Find the items with which the attendee is involved, within the period.

    resource_freebusy = sqlstore.tuples((
        not_freebusy, [store.ns["dtstart"], store.ns["dtend"]], store.ns["datetime"], limit
        ), ordering="asc")

    # Write out the item durations.

    current_start = []
    for item, date_type, _datetime, date in resource_freebusy:
        if date_type == store.ns["dtstart"]:
            current_start.append(date)
        else:
            if current_start:
                start_date = current_start.pop()
            else:
                start_date = start
            if start_date:
                writer.write_attribute("FREEBUSY", value=("%s/%s" % (start_date, date)))

    if current_start and end:
        writer.write_attribute("FREEBUSY", value=("%s/%s" % (current_start[0], end)))

    # Write the footer.

    writer.end_element("VFREEBUSY")
    writer.end_element("VCALENDAR")

# vim: tabstop=4 expandtab shiftwidth=4
