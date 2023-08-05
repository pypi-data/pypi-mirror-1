Introduction
------------

WebOrganiser is a distribution of Web applications providing access to data
stores containing calendars, contact information, messages and potentially
many other kinds of information. The distribution provides two applications,
WebCalendar and WebCalendarPortal, of which only WebCalendar is currently
usable in any meaningful sense.

WebCalendar shows things like events, to-do items, business cards and journal
entries in a Web interface, where you can navigate through them either in a
list or in a month calendar view, selecting, editing, creating, deleting and
exporting them (as iCalendar data) and so on. The experience may be described
as being like using a personal information manager (PIM) like Outlook,
Evolution, Kontact and so on, although you should note that WebCalendar is not
yet ready for production use. It is intended that WebCalendar also integrate
with traditional PIM applications by being able to provide iCalendar
information, including free/busy information that calendar servers like
Exchange and Kolab provide.

WebCalendarPortal attempts to provide a more traditional Web site view onto
the repository of information. Ultimately, it may integrate with WebCalendar
for administrative activities.

Important Note
--------------

Currently, the WebCalendar application is not configured to perform
authentication on users accessing the stored data. It is therefore essential
that for public or shared usage of the application, various changes are made
to the application's configuration in order to deny unauthorised access and to
define authorised user credentials; details of how such configuration may be
performed are provided in the WebStack documentation (see below for the URL
for WebStack), but a simple precaution that may be sufficient for certain
kinds of private use involves specifying 127.0.0.1 or localhost as the
application server's --host option (see below for an example), thus limiting
access to users or clients on the same machine.

Quick Start
-----------

A database must be created to store the information managed by the
WebOrganiser applications. For PostgreSQL, this would be done as follows:

createdb testdb

For sqlite3, no such step is required, since sqltriples can create the
database automatically.

Then, the database must be initialised for use by sqltriples. For example:

sqltriples_admin.py --database=testdb --module=PgSQL --init

Or for sqlite3:

sqltriples_admin.py --database=testdb --module=pysqlite2 --init

Provided the dependencies have been installed, it should be possible to start
the WebCalendar application, specifying a store name and a store type as
follows:

python start.py --store=testdb --module=PgSQL

The above command opens a database called testdb using sqltriples; this
depends on such a database having been created and being accessible to the
user running the command.

After starting the application, visit the following URL in a Web browser:

http://localhost:8080/

To access the WebDAV interface, visit the following URL in a WebDAV-capable
browser or file manager:

webdav://localhost:8080/

To choose a different address for the server, try specifying values for the
--host and --port options to the start.py program. For example:

python start.py --store=testdb --module=PgSQL --host=localhost --port=8081

Contact, Copyright and Licence Information
------------------------------------------

The current Web page for WebOrganiser at the time of release is:

http://www.boddie.org.uk/python/WebOrganiser.html

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/LICENCE.txt for more information.

Dependencies
------------

WebOrganiser has the following basic dependencies:

Package                     Release Information
-------                     -------------------

RDFCalendar                 0.2.3
RDFMessage                  0.1.1
RDFFormats                  0.1.1
XSLTools                    0.4.4
WebStack                    1.2.2
libxml2dom                  0.3.3
CMDsyntax                   0.91
sqltriples                  0.3.1

URLs
----

RDFCalendar                 http://www.boddie.org.uk/python/RDFCalendar.html
RDFMessage                  http://www.boddie.org.uk/python/RDFMessage.html
RDFFormats                  http://www.boddie.org.uk/python/RDFFormats.html
XSLTools                    http://www.boddie.org.uk/python/XSLTools.html
WebStack                    http://www.boddie.org.uk/python/WebStack.html
libxml2dom                  http://www.boddie.org.uk/python/libxml2dom.html
CMDsyntax                   http://www.boddie.org.uk/david/Projects/Python/CMDSyntax/index.html
sqltriples                  http://www.boddie.org.uk/python/sqltriples.html

New in WebOrganiser 0.2.4 (Changes since WebOrganiser 0.2.3)
------------------------------------------------------------

  * Fixed transactions around various store operations.
  * Added some support for event times.
  * Changed encodings usage to take advantage of WebStack 1.2.2 and the
    EncodingSelector class.
  * Added feedback about which item types are being shown.
  * Added last modified items to the calendar view (already listed in the
    property list view).
  * Fixed item collection export for "all.ics".
  * Updated dependencies to fix deep removal of items (and the erroneous
    deletion of connected resources).

New in WebOrganiser 0.2.3 (Changes since WebOrganiser 0.2.2)
------------------------------------------------------------

  * Added depth filtering, rejecting depth infinity PROPFIND requests.
  * Simplified the site map, removing the flexible URL processing at the item
    level, now redundant due to the "stable" location of scripts and styles.
  * Fixed the paths used by related-to and other collection items (fixing a
    problem introduced in the 0.2.2 redirections fix).
  * Added primitive OPTIONS method support.

New in WebOrganiser 0.2.2 (Changes since WebOrganiser 0.2.1)
------------------------------------------------------------

  * Fixed redirections so that the complete URL is taken into consideration.
  * Changed the default datetime in the portal application.
  * Updated the sqltriples dependency to avoid query problems.
  * Added CGI support. 

New in WebOrganiser 0.2.1 (Changes since WebOrganiser 0.2)
----------------------------------------------------------

  * Removed the explicit "root" URL setting, making use of the WebStack
    PathSelector resource.
  * Removed superfluous redirect logic in the TopLevelSelector class.

New in WebOrganiser 0.2 (Changes since WebOrganiser 0.1.4)
----------------------------------------------------------

  * Moved RDFAccess to the new WebOrganiser package.
  * Reduced dependencies on RDFCalendar, specifically changing RDFAccess to
    use a generic store (with certain conveniences) and specially registered
    handlers, of which RDFCalendar is one.
  * Added WebCalendarPortal - an alternative presentation of calendar data.
  * Fixed URL-encoding of / and # characters.
  * Fixed PROPFIND responses, particularly those for collection export
    resources, leaf resources and paths employed in the root template.
  * Made /date/year redirect to /date/year/.
  * Added free/busy information export.
  * Reverted date marking (next day values) in the event editing mechanisms
    in order to simplify date verification and to prevent the introduction of
    invalid dates.
  * Changed much of the querying to use RDFFormats mechanisms.
  * Introduced a "root" URL setting to make images available from a common
    location, thus improving efficiency and performance.

New in WebOrganiser 0.1.4 (Changes since WebOrganiser 0.1.3)
------------------------------------------------------------

  * Added options to change the application server's address.
  * Rearranged the URL namespace so that filtering must be combined with
    type-related path components, thus permitting the viewing of different
    item types in conjunction with filters along, with the creation of new
    items conforming to the filter criteria (currently only related-to
    criteria).
  * Introduced created, dtstamp and related-to information into new items,
    adding the missing related-to element to events.
  * Added checks to new event and to-do item creation, ensuring that they
    employ URIRef rather than BNode objects, since such items may be
    referenced by other items.
  * Added a new "continued" image, used in the item calendar view to more
    easily distinguish continued events from other items.
  * Fixed the WebDAV views to show proposed filtering items, resulting
    filtered information, and other navigation criteria correctly, according
    to the revised URL namespace.
  * Changed timestamps to use UTC.
  * Added journal support.
  * Introduced sqltriples-based querying for filter operations.
  * Added navigation between list and calendar views.
  * Improved translations in various screens.
  * Made resource selection stricter, causing HTTP 404 responses for
    inappropriate URLs.
  * Improved month navigation in the event (and journal) editors, also
    providing a visual indication of the day today.

New in WebOrganiser 0.1.3 (Changes since WebOrganiser 0.1.2)
------------------------------------------------------------

  * Added missing copyright and licensing notices.
  * Added support for Crystal SVG icons.

New in WebOrganiser 0.1.2 (Changes since WebOrganiser 0.1.1)
------------------------------------------------------------

  * Improved handling of imported resources, returning more accurate (or more
    conformant) status codes.
  * Simplified person searching in event and to-do item editing; added person
    details to the retrieved person items by merging in their contact details.
  * Added event, to-do item and card creation in the calendar view (fixing
    redirects in the item list view).
  * Added a check to prevent cards being created without some kind of URIRef
    being defined. Other item types are also likely to have similar
    restrictions applied.
  * Changed the identifier scheme so that URI references for items belonging
    to a store have unprefixed identifiers, and all other items have prefixed
    identifiers of some kind.
  * Introduced URIRef-based property values, requiring various changes in the
    filtering mechanisms (such as "related-to" and "person").
  * Provided translations for various screens.
  * Added images to the various summary screens, adjusting the layout and
    moving table headers to the "controls" section where possible, and also
    moving/adding links to other item types to the "controls" section.
  * Moved calendar cell marking logic from the event template to a special
    transformation used in the editor resource. Added marking of cells to the
    items calendar view.
  * Fixed POST request direction to viewers where filtering is in use.
  * Fixed hCalendar information in the item list view, and added such
    information to the item calendar view.
  * Changed calendar month navigation in the event editor view, requiring the
    reselection of dates where month navigation occurs, since this makes the
    behaviour of the application somewhat more predictable.

New in WebOrganiser 0.1.1 (Changes since WebOrganiser 0.1)
----------------------------------------------------------

  * Added event, to-do item and card creation.
  * Fixed various editing and saving operations.

Release Procedures
------------------

Update the WebOrganiser/__init__.py, applications/WebCalendar/__init__.py and
applications/WebCalendarPortal/__init__.py __version__ attributes.
Change the version number and package filename/directory in the documentation.
Change code examples in the documentation if appropriate.
Update the release notes (see above).
Check the setup.py file and ensure that all package directories are
mentioned.
Check the release information in the PKG-INFO file and in the package
changelog (and other files).
Tag, export.
(Generate the API documentation.)
Generate the application resources.
Prepare the application images.
Remove generated .pyc files: rm `find . -name "*.pyc"`
Archive, upload.
(Upload the introductory documentation.)
Update PyPI entry.

Generating the Application Resources
--------------------------------

In order to prepare the example resources, the prepare_resources.py script
must be run as follows:

python tools/prepare_resources.py

This will ensure that all initialiser and output stylesheets are created and
are thus installed by packages.

Preparing the Application Images
--------------------------------

To ensure that images are available in the application, the prepare_images.py
script must be run as follows:

python tools/prepare_images.py --copy

Where necessary, specific information about the whereabouts, sizes and nature
of icons can be specified as options to the program.

Making Packages
---------------

To make Debian-based packages:

  1. Create new package directories under packages if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/ubuntu-hoary/python2.4-weborganiser/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
