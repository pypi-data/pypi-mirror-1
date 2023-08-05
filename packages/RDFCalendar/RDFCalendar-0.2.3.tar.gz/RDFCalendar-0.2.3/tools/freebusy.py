#!/usr/bin/env python

"""
Export free/busy information for a person or resource.

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

# Main program.

if __name__ == "__main__":
    import cmdsyntax
    import sys
    import codecs
    import RDFCalendar.Store
    import RDFCalendar.Parsers
    from RDFCalendar.Writers import write_freebusy
    import sqltriples

    # Find the documents.

    syntax = cmdsyntax.Syntax("""
        --store=STORE_NAME
        --store-type=STORE_TYPE
        [--module=MODULE]
        [--context=NAMESPACE]
        ( ( --organiser=ORGANISER --attendee=URI [--start-date=START] [--end-date=END] )
          | --input-ics=INPUT_FILE )
        --output-ics=OUTPUT_FILE
        [--attendee-as-organiser]
        [--compact]
        [--quopri]
        [--badfold]
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
        print "  STORE_TYPE         The store type: sqltriples."
        print "  MODULE             The sqltriples module to be used: PgSQL or pysqlite2."
        print "  NAMESPACE          A context namespace."
        print "  ORGANISER          The identity, typically an URI, of the requester."
        print "  URI                The URI representing the person or resource whose free/busy"
        print "                     details shall be exported."
        print "  START              The start date in iCalendar notation."
        print "  END                The end date in iCalendar notation."
        print "  INPUT_FILE         An iCalendar FREEBUSY request."
        print "  OUTPUT_FILE        The iCalendar FREEBUSY response."
        print
        print "Examples:"
        print
        print "  python tools/freebusy.py --store=testdb --store-type=sqltriples --module=PgSQL \\"
        print "    --organiser=MAILTO:paul@boddie.org.uk --attendee=MAILTO:paul@boddie.org.uk \\"
        print "    --output-ics=tmp.ics"
        sys.exit(1)

    # Open a store.

    store = RDFCalendar.Store.open(args["store"], args["store-type"], args.get("context"), database_module_name=args.get("module"))
    try:
        if not getattr(store.store, "supports_querying", 0):
            print "Store type", args["store-type"], "does not support querying, which is necessary"
            print "to provide free/busy export."
            raise SystemExit

        f = codecs.open(args["output-ics"], "wb", encoding="utf-8")
        compact=args.has_key("compact")
        use_quoted_printable=args.has_key("quopri")
        fold_incorrectly=args.has_key("badfold")
        attendee_as_organiser=args.has_key("attendee-as-organiser")

        if args.has_key("input-ics"):
            fi = codecs.open(args["input-ics"], "rb", encoding="utf-8")
            request = RDFCalendar.Store.FreeBusyRequest()
            RDFCalendar.Parsers.parse(fi, request)
            fi.close()
            start, end, organiser, attendee = request.start, request.end, request.organiser, request.attendee
        else:
            start = args.get("start-date")
            end = args.get("end-date")
            organiser = args["organiser"]
            attendee = args["attendee"]

        write_freebusy(f, store, start, end, organiser, attendee, attendee_as_organiser, compact, use_quoted_printable, fold_incorrectly)
        f.close()

    finally:
        store.close()

# vim: tabstop=4 expandtab shiftwidth=4
