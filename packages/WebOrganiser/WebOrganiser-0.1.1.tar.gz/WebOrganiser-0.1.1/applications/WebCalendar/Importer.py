#!/usr/bin/env python

"""
Importer classes.

Copyright (C) 2005, 2006 Paul Boddie <paul@boddie.org.uk>

This software is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with this library; see the file LICENCE.txt
If not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

from WebStack.Generic import ContentType, EndOfResponse
import RDFCalendar.Parsers
import urllib
import codecs
import os

class ItemImporterResource:

    "An item importer."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    path_encoding = "utf-8"

    def __init__(self, store):
        self.store = store

    def respond(self, trans):

        # Get the name and type of the file.

        attributes = trans.get_attributes()
        item_type_name = attributes["item-type"]
        item_value = attributes["item-value"]

        # NOTE: Assuming UTF-8 input. Check the actual uploaded data!

        in_stream = codecs.getreader(self.encoding)(trans.get_request_stream())

        # Prepare a response, regardless of the outcome.

        trans.set_content_type(ContentType("text/plain", self.encoding))
        stream = trans.get_response_stream()

        # NOTE: Should issue various "moved" status responses if the uploaded
        # NOTE: resource doesn't match the item type.

        try:
            if trans.get_request_method() == "PUT":

                # URIs must be quoted. It is quite likely that the name used
                # was not doubly-encoded and contains characters outside the
                # ASCII subset.

                uriref = self.store.URIRef(urllib.quote(item_value))

                # Read the uploaded data.

                RDFCalendar.Parsers.parse(in_stream, self.store.cstore, name=item_value, uriref=uriref)
                self.store.commit()
                stream.write("Thank you for the file, %s." % item_value)

            elif trans.get_request_method() == "DELETE":

                # Remove the identified item.

                item = self.store.get_item_from_identifier(item_value)
                self.store.remove_item(item, deep=1)
                self.store.commit()
                stream.write("Item %s deleted." % item_value)

            # Disallow other methods.

            else:
                trans.set_response_code(405)
                stream.write("Method not allowed")

        except:
            trans.set_response_code(500)
            stream.write("Could not accept the file, %s." % item_value)
            raise # EndOfResponse

        raise EndOfResponse

# vim: tabstop=4 expandtab shiftwidth=4
