Introduction
------------

RDFCalendar is a package providing support for the parsing of iCalendar and
vCard resources (in their native formats and as XML representations), the
conversion of such resources to RDF-based information, and the extraction of
such information in iCalendar, vCard and XML formats.

Quick Start
-----------

For use with sqltriples, a suitable store must first be initialised in a
suitable database system - see the sqltriples documentation for details.

Try importing a calendar file into an sqltriples store in the file tmp:

python tools/iCalendar.py --store=tmp --store-type=sqltriples \
  --module=pysqlite2 --uriref=MyCalendar --input-ics=calendar.ics

Try exporting a calendar as XML:

python tools/iCalendar.py --store=tmp --store-type=sqltriples \
  --module=pysqlite2 --uriref=MyCalendar --output-xml=calendar.xml

Try exporting a calendar in iCalendar format:

python tools/iCalendar.py --store=tmp --store-type=sqltriples \
  --module=pysqlite2 --uriref=MyCalendar --output-ics=calendar-out.ics

Contact, Copyright and Licence Information
------------------------------------------

The current Web page for RDFCalendar at the time of release is:

http://www.boddie.org.uk/python/RDFCalendar.html

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/LICENCE.txt for more information.

Dependencies
------------

RDFCalendar has the following basic dependencies:

Package                     Release Information
-------                     -------------------

RDFFormats                  0.1.1
libxml2dom                  0.3.3
sqltriples                  0.3
CMDsyntax                   Tested with 0.91

URLs
----

RDFFormats                  http://www.boddie.org.uk/python/RDFFormats.html
libxml2dom                  http://www.boddie.org.uk/python/libxml2dom.html
sqltriples                  http://www.boddie.org.uk/python/sqltriples.html
CMDsyntax                   http://www.boddie.org.uk/david/Projects/Python/CMDSyntax/index.html

New in RDFCalendar 0.2.3 (Changes since RDFCalendar 0.2.2)
----------------------------------------------------------

  * Updated the RDFFormats dependency to fix the deep removal issue properly.

New in RDFCalendar 0.2.2 (Changes since RDFCalendar 0.2.1)
----------------------------------------------------------

  * Added "organizer" and "attendee" to the list of connector labels,
    preventing deep removal of related resources.

New in RDFCalendar 0.2.1 (Changes since RDFCalendar 0.2)
--------------------------------------------------------

  * Exclude free/busy items in the calculation of free/busy information
    (RDFCalendar.Writers).

New in RDFCalendar 0.2 (Changes since RDFCalendar 0.1.4)
--------------------------------------------------------

  * Introduced a dependency on RDFFormats which provides more general support
    for store-like functionality useful for parsers and writers. As a
    consequence, the interface to store functionality is more explicit for
    parsing operations, store-level convenience methods are removed, and
    various "handler" methods are exposed that are useful for querying the
    store about the kinds of nodes and namespaces it supports, as well as for
    performing parsing and serialisation operations.
  * Added free/busy export support, along with a simple store-like class for
    the acquisition of free/busy request information, and a special writer
    function for writing response information to a stream.
  * Added the rdfcalendar namespace text to the top-level RDFCalendar module.
  * Fixed/improved multivalue support, also adding period value support.
  * Dropped rdflib support.

New in RDFCalendar 0.1.4 (Changes since RDFCalendar 0.1.3)
----------------------------------------------------------

  * Changed make_uid to return supplied "general" URIs as usable unique
    identifiers for the data store. Since the returned unique identifiers are
    otherwise full URIs themselves, it is desirable to treat "general" URIs
    equivalently.
  * Fixed the iCalendar import/export tool to work with sqltriples 0.2.x.
  * Added a test to prevent (failed) serialisation of non-calendar resources.
  * Fixed handling of "end of file" lines without newline characters.

New in RDFCalendar 0.1.3 (Changes since RDFCalendar 0.1.2)
----------------------------------------------------------

  * Added RDFCalendar.Format.uriref_labels and made certain property values
    URIRef objects rather than Literal objects.
  * Changed the RDFCalendar.Store.open convenience function to pass on
    received keyword parameters to sqltriples.

New in RDFCalendar 0.1.2 (Changes since RDFCalendar 0.1.1)
----------------------------------------------------------

  * Empty values for related-to properties are no longer recorded in the data
    store.

New in RDFCalendar 0.1.1 (Changes since RDFCalendar 0.1)
--------------------------------------------------------

  * Added checks for duplicate resources in the parsers, raising an exception
    if an attempt is made to parse a resource using an URIRef which is already
    known to the store.

Release Procedures
------------------

Update the RDFCalendar/__init__.py __version__ attributes.
Change the version number and package filename/directory in the documentation.
Change code examples in the documentation if appropriate.
Update the release notes (see above).
Check the setup.py file and ensure that all package directories are mentioned.
Check the release information in the PKG-INFO file and in the package
changelog (and other files).
Tag, export.
Generate the API documentation.
Remove generated .pyc files: rm `find . -name "*.pyc"`
Archive, upload.
(Upload the introductory documentation.)
Update PyPI entry.

Generating the API Documentation
--------------------------------

In order to prepare the API documentation, it is necessary to generate some
Web pages from the Python source code. For this, the epydoc application must
be available on your system. Then, inside the distribution directory, run the
apidocs.sh tool script as follows:

./tools/apidocs.sh

Some warnings may be generated by the script, but the result should be a new
apidocs directory within the distribution directory.

Making Packages
---------------

To make Debian-based packages:

  1. Create new package directories under packages if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/ubuntu-hoary/python2.4-rdfcalendar/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
