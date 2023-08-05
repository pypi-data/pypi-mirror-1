#!/usr/bin/env python

"""
Format writer classes.

Copyright (C) 2005, 2006 Paul Boddie <paul@boddie.org.uk>

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

from RDFCalendar.Format import *
import RDFFormats.FormatWriters

class iCalendarWriter:

    "An iCalendar writer class."

    def __init__(self, f, compact=0, use_quoted_printable=0, fold_incorrectly=0, do_not_fold=0):

        """
        Initialise the writer with a stream 'f', configuring the writer with the
        following optional parameters:

          * compact              - use a compact representation (popular with
                                   many applications, but not enabled by
                                   default)
          * use_quoted_printable - use the quoted-printable representation for
                                   text (not enabled by default)
          * fold_incorrectly     - produce incorrectly folded text to satisfy
                                   non-compliant applications (not enabled by
                                   default)
          * do_not_fold          - do not fold text but place long text on a
                                   single line (not enabled by default)
        """

        self.f = f
        self.compact = compact
        self.use_quoted_printable = use_quoted_printable
        self.fold_incorrectly = fold_incorrectly
        self.do_not_fold = do_not_fold
        self.line_length = 76

    def start_element(self, label):
        self.f.write("BEGIN:%s\r\n" % label)

    def end_element(self, label):
        self.f.write("END:%s\r\n" % label)

    def write_attribute(self, name, modifiers=None, value=None, subvalues=None, multivalues=None):
        if self.compact:
            self.f.write(name)
        else:
            self.f.write(name + "\r\n")

        # Where quoted printable is used, sneak in a modifier.
        # NOTE: Only supported for single value attributes.
        # NOTE: Assume that the value should be ISO 8859-1.
        # NOTE: Also assume that the quopri stuff uses only LF and not CRLF.

        modifiers = modifiers or []
        if value is not None:
            if self.use_quoted_printable:
                try:
                    value = value.encode("US-ASCII").replace("\n", "=0A")
                except UnicodeError:
                    modifiers.append(("ENCODING", "QUOTED-PRINTABLE"))

                    # NOTE: Nasty recoding of newlines to avoid confusion with
                    # NOTE: those introduced by encodestring.

                    value = value.replace("\n", "\\n")
                    value = quopri.encodestring(value.encode("iso-8859-1"))

                    # NOTE: Explicit conversions.

                    value = value.replace("\\n", "=0A")
                    value = value.replace("\n", "\r\n")
            else:
                # NOTE: Introducing newline conversions.

                value = value.replace("\n", "\\n")

        if modifiers is not None:
            for modifier_name, modifier_value in modifiers:
                if self.compact:
                    self.f.write(";" + modifier_name + "=" + modifier_value)
                else:
                    self.f.write(" ;" + modifier_name + "=" + modifier_value + "\r\n")

        if value is not None:
            if self.compact:
                self.f.write(":")
            else:
                self.f.write(" :")
            self.f.write(self.get_folded_lines(value) + "\r\n")

        elif subvalues is not None:
            assignments = [(name + "=" + value) for (name, value) in subvalues]
            if self.compact:
                self.f.write(":")
            else:
                self.f.write(" :")
            self.f.write(";".join(assignments) + "\r\n")

        elif multivalues is not None:
            if self.compact:
                self.f.write(":")
            else:
                self.f.write(" :")
            l = []
            for multivalue in multivalues:
                if multivalue.has_key("END"):
                    l.append("%s/%s" % (multivalue["START"], multivalue["END"]))
                elif multivalue.has_key("DURATION"):
                    l.append("%s/%s" % (multivalue["START"], multivalue["DURATION"]))
                else:
                    l.append(multivalue["DETAILS"])
            self.f.write(",".join(l) + "\r\n")

    def close(self):
        self.f.close()

    def get_folded_lines(self, value):
        if self.do_not_fold:
            return value
        if not self.fold_incorrectly:
            value = value.replace("\r\n", "\r\n ")
        new_lines = []
        for line in value.split("\r\n"):
            self.add_folded_lines(line, new_lines)
        return "\r\n".join(new_lines)

    def add_folded_lines(self, line, lines):
        lines.append(line[:self.line_length])
        for i in range(self.line_length, len(line), self.line_length):
            limit = min(i + self.line_length, len(line))
            new_line = line[i:limit]
            if not self.fold_incorrectly:
                lines.append(" " + new_line)
            else:
                lines.append(new_line)

class DOMWriter(RDFFormats.FormatWriters.DOMWriter):

    "A DOM document writer."

    def get_item_type_name(self, label):
        return element_names[label]

    def get_property_name(self, attribute_name):
        return attribute_name.lower()

    def get_property_label(self, property_name):
        return get_property_label(property_name)

# vim: tabstop=4 expandtab shiftwidth=4
