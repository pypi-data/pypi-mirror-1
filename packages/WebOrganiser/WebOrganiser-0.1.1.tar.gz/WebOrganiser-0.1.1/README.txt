Introduction
------------

WebOrganiser is a distribution of Web applications providing access to data
stores containing calendars, contact information, messages and potentially
many other kinds of information.

Quick Start
-----------

Provided the dependencies have been installed, it should be possible to start
the WebCalendar application, specifying a store name and a store type as
follows:

python start.py my-store rdflib

The above command creates a file called my-store using rdflib, and on
subsequent usage of the WebCalendar application, this file will be opened.
Alternatively, an sqltriples-resident data store can be used; for example:

python start.py testdb sqltriples

The above command opens a database called testdb using sqltriples; this
depends on such a database having been created and being accessible to the
user running the command.

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

RDFCalendar                 0.1
XSLTools                    0.4
WebStack                    1.1.2
libxml2dom                  0.3.3

New in WebOrganiser 0.1.1 (Changes since WebOrganiser 0.1)
----------------------------------------------------------

  * Added event, to-do item and card creation.
  * Fixed various editing and saving operations.

Release Procedures
------------------

Update the applications/WebCalendar/__init__.py __version__ attribute.
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
