#!/usr/bin/env python

"""
Exporter classes.

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
import codecs
import os
import datetime
import RDFCalendar

class ItemExporterResource:

    "An event/to-do item exporter."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"

    def __init__(self, store):
        self.store = store

    def respond(self, trans):

        # Determine which item is being exported.

        attributes = trans.get_attributes()
        item_value = attributes["item-value"]
        item = self.store.get_item_from_identifier(item_value)

        # Detect the item type (since the path information may not be appropriate).

        item_type = self.store.get_item_type(item)
        item_type_name = self.store.get_identifier_from_item_type(item_type)

        # Start the response.

        stream = codecs.getwriter(self.encoding)(trans.get_response_stream())

        # NOTE: Try and generalise the mechanisms here so that the media type
        # NOTE: is obtained from the format handler.
        # Export calendars as they are.

        if item_type_name == "calendar":
            trans.set_content_type(ContentType("text/calendar", self.encoding))
            self.store.serialise_item(item, stream)
            raise EndOfResponse

        # Export cards directly.

        elif item_type_name == "card":
            trans.set_content_type(ContentType("text/card", self.encoding))
            self.store.serialise_item(item, stream)
            raise EndOfResponse

        # Export messages directly.

        elif item_type_name == "e-mail":
            trans.set_content_type(ContentType("text/plain", self.encoding))
            self.store.serialise_item(item, stream)
            raise EndOfResponse

        # Export calendar items inside special enclosures.

        else:
            trans.set_content_type(ContentType("text/calendar", self.encoding))
            stream.write("BEGIN:VCALENDAR\n")
            stream.write("PRODID\n :-//RDFCalendar//NONSGML WebOrganiser//EN\n")
            stream.write("VERSION\n :2.0\n")
            self.store.serialise_item(item, stream)
            stream.write("END:VCALENDAR\n")
            raise EndOfResponse

class CollectionExporterResource:

    "A item collection exporter."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"

    def __init__(self, store):
        self.store = store

    def respond(self, trans):

        # Determine the details of the collection.

        attributes = trans.get_attributes()
        found_items = self.store.get_items_using_attributes(attributes)

        # Start the response.

        stream = codecs.getwriter(self.encoding)(trans.get_response_stream())

        # Export calendar items inside special enclosures.

        trans.set_content_type(ContentType("text/calendar", self.encoding))
        export_items(found_items, self.store, stream)
        raise EndOfResponse

class FreeBusyExporterResource:

    "A free/busy information exporter."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"

    def __init__(self, store):
        self.store = store

    def respond(self, trans):

        # Determine the details of the collection.

        attributes = trans.get_attributes()

        # Get the start and end dates according to date filtering details.

        year, month, day = attributes.get("year"), attributes.get("month") or 1, attributes.get("day") or 1

        if year is not None:
            start_date = datetime.datetime(year, month, day)
            if day is not None:
                end_date = start_date + datetime.timedelta(days=1)
            elif month is not None:
                end_date = start_date + datetime.timedelta(months=1)
            else:
                end_date = start_date + datetime.timedelta(years=1)
            start = start_date.strftime("%Y%m%d")
            end = end_date.strftime("%Y%m%d")
        else:
            start, end = None, None

        # Get the attendee information according to any person filter criteria.

        if attributes.get("filter-type") == "person":
            attendee = self.store.get_item_from_identifier(attributes["filter-item-value"])
        else:
            trans.set_content_type(ContentType("text/plain"))
            trans.get_response_stream().write("No person specified.")
            raise EndOfResponse

        organiser = attendee # NOTE: To be changed to be the user.

        # Start the response.

        stream = codecs.getwriter(self.encoding)(trans.get_response_stream())

        # Export calendar items inside special enclosures.

        trans.set_content_type(ContentType("text/calendar", self.encoding))
        RDFCalendar.Writers.write_freebusy(stream, self.store.get_handler_for_item_type_name("free-busy"), start, end, organiser, attendee)
        raise EndOfResponse

def export_items(found_items, store, stream):
    #stream.write("BEGIN:VCALENDAR\n")
    #stream.write("PRODID\n :-//RDFCalendar//NONSGML WebOrganiser//EN\n")
    #stream.write("VERSION\n :2.0\n")
    for item in found_items:
        #item_type = store.get_item_type(item)
        #item_type_name = store.get_identifier_from_item_type(item_type)
        store.serialise_item(item, stream)
    #stream.write("END:VCALENDAR\n")

# vim: tabstop=4 expandtab shiftwidth=4
