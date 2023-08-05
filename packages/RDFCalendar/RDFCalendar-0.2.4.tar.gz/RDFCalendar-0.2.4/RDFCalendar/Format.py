#!/usr/bin/env python

"""
Constants for parsing and writing.

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

# Plain rdfcalendar and other namespaces.

rdfcalendar = "http://www.boddie.org.uk/ns/rdfcalendar/"
rdftype = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

# Element names.

element_names = {
    "VCALENDAR" : "calendar",
    "VEVENT" : "event",
    "VTODO" : "to-do",
    "VJOURNAL" : "journal",
    "VFREEBUSY" : "free-busy",
    "VTIMEZONE" : "timezone",
    "VALARM" : "alarm",
    "VCARD" : "card"
    }

# A reverse mapping from element/item type names to element names.
# See below for supported item types in a narrower context.

item_type_names = {}
for key, value in element_names.items():
    item_type_names[value] = key

# Permitted elements within elements.

permitted_elements = {
    "VCALENDAR" : ("VEVENT", "VTODO", "VJOURNAL", "VFREEBUSY", "VTIMEZONE"),
    "VEVENT" : ("VALARM",),
    "VTODO" : ("VALARM",),
    "VJOURNAL" : (),
    "VFREEBUSY" : (),
    "VTIMEZONE" : (),
    "VALARM" : (),
    "VCARD" : ()
    }

permitted_attributes = {
    "VCALENDAR" : ("VERSION", "CALSCALE", "METHOD", "PRODID"),
    "VEVENT" : ("CLASS", "CREATED", "DESCRIPTION", "DTSTAMP", "DTSTART", "GEO",
        "LAST-MODIFIED", "LOCATION", "ORGANIZER", "PRIORITY", "RECURRENCE-ID",
        "SEQUENCE", "STATUS", "SUMMARY", "TRANSP", "UID", "URL",
        "DTEND", "DURATION",
        "ATTACH", "ATTENDEE", "CATEGORIES", "COMMENT", "CONTACT",
        "EXDATE", "EXRULE", "RDATE", "RELATED-TO", "RESOURCES",
        "REQUEST-STATUS", "RRULE"),
    "VTODO" : ("CLASS", "COMPLETED", "CREATED", "DESCRIPTION", "DTSTAMP",
        "DTSTART", "GEO", "LAST-MODIFIED", "LOCATION", "ORGANIZER", "PERCENT-COMPLETE",
        "PRIORITY", "RECURRENCE-ID", "SEQUENCE", "STATUS", "SUMMARY", "UID",
        "URL", "DUE", "DURATION",
        "ATTACH", "ATTENDEE", "CATEGORIES", "COMMENT", "CONTACT", "EXDATE",
        "EXRULE", "REQUEST-STATUS", "RELATED-TO", "RESOURCES", "RDATE",
        "RRULE"),
    "VJOURNAL" : ("CLASS", "CREATED", "DESCRIPTION", "DTSTART", "DTSTAMP",
        "LAST-MODIFIED", "ORGANIZER", "RECURRENCE-ID", "SEQUENCE", "STATUS",
        "SUMMARY", "UID", "URL",
        "ATTACH", "ATTENDEE", "CATEGORIES", "COMMENT", "CONTACT", "EXDATE",
        "EXRULE", "RELATED-TO", "RDATE", "RRULE", "REQUEST-STATUS"),
    "VFREEBUSY" : ("CONTACT", "DTSTAMP", "DTSTART", "DTEND", "DURATION",
        "ORGANIZER", "UID", "URL",
        "ATTENDEE", "COMMENT", "FREEBUSY", "REQUEST-STATUS"),
    "VTIMEZONE" : ("TZID",
        "LAST-MODIFIED", "TZURL",
        "DTSTART", "TZOFFSETTO", "TZOFFSETFROM",    # Standard/daylight
        "COMMENT", "RDATE", "RRULE", "TZNAME"),     # Standard/daylight
    "VALARM" : ("ACTION", "TRIGGER",                # Audio/display/e-mail/procedure
        "DURATION", "REPEAT",                       # Audio/display/e-mail/procedure
        "DESCRIPTION",                              # Display/e-mail/procedure
        "ATTACH",                                   # E-mail
        "ATTENDEE"),                                # E-mail
    "VCARD" : ("ADR", "CLASS", "EMAIL", "FN", "LABEL", "N", "NOTE", "ORG",
        "ROLE", "TEL", "UID", "URL", "VERSION")
    }

# Special attributes.

person_attributes = ("ATTENDEE", "ORGANIZER")
datetime_attributes = ("COMPLETED", "CREATED", "DTSTAMP", "DTSTART", "DTEND", "DUE", "LAST-MODIFIED")
datetime_values = ("UNTIL",)
subvalue_attributes = ("RRULE", "EXRULE")
multivalue_attributes = ("RDATE", "EXDATE")
connector_attributes = ("RELATED-TO",)
period_attributes = ("FREEBUSY",) # also multivalue

# Attribute labels.

permitted_labels = {}
for value in person_attributes:
    permitted_labels[value.lower()] = "uri"
for value in datetime_attributes:
    permitted_labels[value.lower()] = "datetime"
for value in connector_attributes:
    permitted_labels[value.lower()] = "uri"

# Label types.

connector_labels = ["related-to", "organizer", "attendee"]
uriref_labels = ["uri", "related-to"]
value_labels = ["start", "duration", "end", "datetime", "uri", "details", "related-to", "contains", "name"]

# A collection of all supported attributes as labels.

all_labels = []
for key, values in permitted_attributes.items():
    for value in values:
        label = value.lower()
        if label not in all_labels:
            all_labels.append(label)

# Supported item types.

supported_item_types = ["card", "calendar", "event", "free-busy", "to-do", "journal"]

# Format helper functions.

def get_property_label(property_name):

    """
    Return the special property label for the given 'property_name', or None
    if a generic label is to be used (for example, to construct a predicate for
    RDF triple stores).
    """

    return permitted_labels.get(property_name)

# vim: tabstop=4 expandtab shiftwidth=4
