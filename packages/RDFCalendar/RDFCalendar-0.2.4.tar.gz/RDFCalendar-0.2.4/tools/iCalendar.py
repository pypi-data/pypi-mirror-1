#!/usr/bin/env python

"""
Import or export items from data stores.

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

import RDFCalendar.Store
import RDFCalendar.Parsers
import RDFCalendar.Writers
import RDFCalendar.FormatWriters

# Main program.

if __name__ == "__main__":
    import cmdsyntax
    import sys
    import codecs
    import libxml2dom

    # Find the documents.

    syntax = cmdsyntax.Syntax("""
        --store=STORE_NAME
        --store-type=STORE_TYPE
        [--module=MODULE]
        [(--contexts | --context=NAMESPACE)]
        [--name=NAME]
        [--uriref=URIREF]
        [--input-ics=INPUT_FILE]
        [--input-encoding=ENCODING]
        [--input-xml=INPUT_FILE]
        [--output-rdf=OUTPUT_FILE]
        [--output-ics=OUTPUT_FILE]
        [--output-xml=OUTPUT_FILE]
        [--output-xml-value-attr]
        [--compact]
        [--quopri]
        [--badfold]
        [--cr]
        [--remove]
        [--remove-context]
        """)

    syntax_matches = syntax.get_args(sys.argv[1:])

    try:
        args = syntax_matches[0]
    except IndexError:
        print "Syntax:"
        print syntax.syntax
        print "Terms:"
        print
        print "  STORE_NAME         The store location or identifier."
        print "  STORE_TYPE         The store type: sqltriples"
        print "  MODULE             The sqltriples module to be used: PgSQL or pysqlite2"
        print "  NAMESPACE          A context namespace."
        print "  NAME               A name property to be assigned to the resource."
        print "  URIREF             The URI representing the resource."
        print "  INPUT_FILE         An input file in one of the supported formats."
        print "  OUTPUT_FILE        An output file in one of the supported formats."
        print "  ENCODING           A character encoding such as utf-8 or iso-8859-1."
        print
        print "Examples:"
        print
        print "  python tools/iCalendar.py --store=testdb --store-type=sqltriples --module=PgSQL \\"
        print "    --uriref=MyCalendar --input-ics=calendar.ics"
        sys.exit(1)

    # Open a store.

    store = RDFCalendar.Store.open(args["store"], args["store-type"], args.get("context"), database_module_name=args.get("module"))

    # Perform the requested operations.

    try:
        # Handle different store contexts, if appropriate.

        if args.has_key("contexts"):
            print "Contexts:"
            for context in store.contexts():
                print context
            sys.exit(0)

        # Parse an iCalendar input file.

        if args.has_key("input-ics") and args.has_key("uriref"):
            if args.has_key("encoding"):
                encoding = args["encoding"]
            else:
                encoding = "utf-8"
            f = codecs.open(args["input-ics"], encoding=encoding)
            print "Added", RDFCalendar.Parsers.parse(
                f, store, name=args.get("name"), uriref=store.URIRef(args["uriref"]),
                non_standard_newline=args.has_key("cr")), "as", args["uriref"]

        # Parse an XML input file.

        if args.has_key("input-xml") and args.has_key("uriref"):
            doc = libxml2dom.parseFile(args["input-xml"])
            print "Added", RDFCalendar.Parsers.parse_document(doc, store, uriref=store.URIRef(args["uriref"])), "as", args["uriref"]

        # Save as RDF if requested.

        if args.has_key("output-rdf"):
            print "RDF/XML output not supported by this store type."

        # Save as iCalendar/vCard if requested.

        if args.has_key("output-ics") and args.has_key("uriref"):
            f = codecs.open(args["output-ics"], "wb", encoding="utf-8")
            RDFCalendar.Writers.write_to_stream(
                f, store, main_node=store.URIRef(args["uriref"]),
                compact=args.has_key("compact"),
                use_quoted_printable=args.has_key("quopri"),
                fold_incorrectly=args.has_key("badfold")
                )
            f.close()

        # Save as XML if requested.

        if args.has_key("output-xml") and args.has_key("uriref"):
            if args.has_key("output-xml-value-attr"):
                doc = RDFCalendar.Writers.get_document(store, store.URIRef(args["uriref"]), value_as_attribute=1)
            else:
                doc = RDFCalendar.Writers.get_document(store, store.URIRef(args["uriref"]))
            f = open(args["output-xml"], "wb")
            doc.toStream(f, encoding="utf-8")
            f.close()

        # Remove from the information store if requested.

        if args.has_key("remove"):
            store.remove_node(store.URIRef(args["uriref"]), deep=1)

        # Remove entire contexts if requested.

        if args.has_key("remove-context"):
            store.remove_context(args["context"])

        store.commit()

    finally:
        store.close()

# vim: tabstop=4 expandtab shiftwidth=4
