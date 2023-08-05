#!/usr/bin/env python

"""
Selector classes.

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

from WebStack.Generic import EndOfResponse
import calendar
import urllib

# Resource classes.

class TopSelectorResource:

    """
    A resource which either redirects to another path or which invokes another
    resource to provide WebDAV listings.
    """

    path_encoding = "utf-8"

    def __init__(self, target, listing_resource):
        self.target = target
        self.listing_resource = listing_resource

    def respond(self, trans):

        # Redirect to a specified resource.

        if trans.get_request_method() == "GET":

            # Redirect to the target.

            trans.redirect(
                trans.encode_path(
                    trans.update_path(trans.get_path_without_query(self.path_encoding), self.target),
                    self.path_encoding
                    )
                )

        # Or provide a special top-level listing.

        elif trans.get_request_method() == "PROPFIND":
            self.listing_resource.respond(trans)
            raise EndOfResponse

        # Disallow other methods.

        else:
            trans.set_response_code(405)
            trans.get_response_stream().write("Method not allowed")
            raise EndOfResponse

class DateSelectorResource:

    """
    A resource which extracts date information from the URL and which then
    dispatches requests to a resource which is able to use such information.
    """

    path_encoding = "utf-8"

    def __init__(self, resource, month_listing_resource):
        self.resource = resource
        self.month_listing_resource = month_listing_resource

    def respond(self, trans):

        vpath = trans.get_virtual_path_info(self.path_encoding)
        vpath_fields = vpath.split("/")

        # Find the date information.

        try:
            # There must be something like the following:
            # /year/
            # /year/month/
            # /year/month/day/
            # /year/month/day/...

            # Find the year.

            if len(vpath_fields) > 1:
                year = int(vpath_fields[1])
            else:
                raise ValueError, "" # Not even a year found.

            # Find the month.

            if len(vpath_fields) == 2:

                # Redirect to inside the year resource.

                trans.redirect(
                    trans.encode_path(
                        trans.get_path_without_query() + "/",
                        self.path_encoding
                        )
                    )

            # No month given?

            elif vpath_fields[2] == "":

                # Provide a month listing if the method is appropriate.

                if trans.get_request_method() == "PROPFIND":

                    # Remove the year.
                    trans.set_virtual_path_info("/" + "/".join(vpath_fields[2:]))

                    self.month_listing_resource.respond(trans)
                    raise EndOfResponse
                else:
                    raise ValueError, "" # No month found.

            else:
                month = int(vpath_fields[2])
                if month < 1 or month > 12:
                    raise ValueError, month

            # Find the day, if set.

            day = None
            if len(vpath_fields) > 3:
                try:
                    day = int(vpath_fields[3])
                except ValueError:

                    # Remove the year and month.
                    trans.set_virtual_path_info("/" + "/".join(vpath_fields[3:]))

                else:
                    day1, ndays = calendar.monthrange(year, month)
                    if day < 1 or day > ndays:
                        raise ValueError, day

                    # Redirect if no more path components follow the day.

                    if len(vpath_fields) <= 4:
                        trans.redirect(
                            trans.encode_path(
                                trans.get_path_without_query() + "/",
                                self.path_encoding
                                )
                            )

                    # Remove the year, month and day.
                    trans.set_virtual_path_info("/" + "/".join(vpath_fields[4:]))

            elif vpath_fields[2] != "":
                trans.redirect(
                    trans.encode_path(
                        trans.get_path_without_query() + "/",
                        self.path_encoding
                        )
                    )
            else:
                raise ValueError, "" # No month found.

        except ValueError:
            trans.set_response_code(404)
            trans.get_response_stream().write("Not found")
            raise EndOfResponse

        # Set the date attributes.

        attributes = trans.get_attributes()
        attributes["year"] = year
        attributes["month"] = month
        attributes["day"] = day

        # Dispatch to the specified resource.

        self.resource.respond(trans)
        raise EndOfResponse

class ViewSelectorResource:

    """
    A resource which dispatches requests to different resources depending on the
    type of view implied by the request method.
    """

    def __init__(self, list_viewer, calendar_viewer, prop_viewer):
        self.list_viewer = list_viewer
        self.calendar_viewer = calendar_viewer
        self.prop_viewer = prop_viewer

    def respond(self, trans):

        "Determine which view should be used."

        # For GET/POST methods, choose a view according to the attributes.

        if trans.get_request_method() in ("GET", "POST"):

            # Test for calendar view information.

            attributes = trans.get_attributes()
            if attributes.has_key("year"):
                self.calendar_viewer.respond(trans)
            else:
                self.list_viewer.respond(trans)
            raise EndOfResponse

        # For PROPFIND methods, choose a view of the properties.

        elif trans.get_request_method() == "PROPFIND":
            self.prop_viewer.respond(trans)
            raise EndOfResponse

        # Disallow other methods.

        else:
            trans.set_response_code(405)
            trans.get_response_stream().write("Method not allowed")
            raise EndOfResponse

class ItemSelectorResource:

    """
    A resource which dispatches requests to different resources depending on
    request method and path information, thus distinguishing between editing,
    viewing, exporting and property viewing operations.
    """

    path_encoding = "utf-8"

    def __init__(self, editor, viewer, importer, exporter, prop_viewer):
        self.editor = editor
        self.viewer = viewer
        self.importer = importer
        self.exporter = exporter
        self.prop_viewer = prop_viewer

    def respond(self, trans):

        """
        Determine if an item is being edited; dispatch to the appropriate
        resource.
        """

        vpath = trans.get_virtual_path_info(self.path_encoding)
        pvpath = trans.get_processed_virtual_path_info(self.path_encoding)
        vpath_fields = vpath.split("/")

        # Start recording useful information.

        attributes = trans.get_attributes()

        # Expect a doubly-"URL encoded" identifier to have been processed.

        item_value = pvpath.split("/")[-1]

        # Either get the item identifier, fully decoding the component.

        if not attributes.has_key("item-value"):
            attributes["item-value"] = urllib.unquote(item_value)

        # Or indicate that the resource is not valid.

        else:
            trans.set_response_code(404)
            trans.get_response_stream().write("Resource not found")
            raise EndOfResponse

        # Handle situations which do not include extra non-identifier
        # information.

        if len(vpath_fields) == 1 or len(vpath_fields) == 2 and (
            vpath_fields[1] == "" or vpath_fields[1] in self.editor.in_page_resources.keys()):

            # For GET methods...

            if trans.get_request_method() == "GET":

                # Serve the underlying resource.

                if len(vpath_fields) == 1:
                    self.exporter.respond(trans)
                    raise EndOfResponse

                # Or serve the view of the resource.

                elif attributes.has_key("filter-type") and not attributes.has_key("item-value"):
                    self.viewer.respond(trans)
                    raise EndOfResponse

                else:
                    self.editor.respond(trans)
                    raise EndOfResponse

            # For PUT and DELETE methods...

            elif trans.get_request_method() in ("PUT", "DELETE"):
                self.importer.respond(trans)
                raise EndOfResponse

            # For POST methods...

            elif trans.get_request_method() == "POST" and len(vpath_fields) > 1:

                # Detect filter view actions.

                if attributes.has_key("filter-type") and not attributes.has_key("item-value"):
                    self.viewer.respond(trans)
                    raise EndOfResponse
                else:
                    self.editor.respond(trans)
                    raise EndOfResponse

            # For PROPFIND methods, provide a special property listing.

            elif trans.get_request_method() == "PROPFIND":
                self.prop_viewer.respond(trans)
                raise EndOfResponse

            # Disallow other methods.

            else:
                trans.set_response_code(405)
                trans.get_response_stream().write("Method not allowed")
                raise EndOfResponse

        # Provide other responses if other parts of the path are found.

        self.viewer.respond(trans)
        raise EndOfResponse

class TypeSelectorResource:

    """
    A resource which detects the item type in the path of requests and which
    sets such information in the request attributes before dispatching such
    requests to another resource.
    """

    path_encoding = "utf-8"

    def __init__(self, viewer):
        self.viewer = viewer

    def respond(self, trans):

        """
        Determine if an item is being edited; dispatch to the appropriate
        resource.
        """

        pvpath = trans.get_processed_virtual_path_info(self.path_encoding)

        # Start recording useful information.

        attributes = trans.get_attributes()
        attributes["item-type"] = pvpath.split("/")[-1]
        self.viewer.respond(trans)
        raise EndOfResponse

class FilterSelectorResource:

    """
    A resource which extracts filtering and item type information from requests
    before dispatching such requests to another resource.
    """

    path_encoding = "utf-8"

    def __init__(self, filter_type, viewer, prop_viewer, default_item_type=None):
        self.filter_type = filter_type
        self.viewer = viewer
        self.prop_viewer = prop_viewer
        self.default_item_type = default_item_type

    def respond(self, trans):

        """
        Determine if an item is being edited; dispatch to the appropriate
        resource.
        """

        vpath = trans.get_virtual_path_info(self.path_encoding)
        vpath_fields = vpath.split("/")

        # Start recording useful information.

        attributes = trans.get_attributes()
        attributes["filter-type"] = self.filter_type

        if len(vpath_fields) != 1 and vpath_fields[1]:

            # Expect a doubly-"URL encoded" identifier.

            item_value = vpath_fields[1]
            attributes["filter-item-value"] = urllib.unquote(item_value)
            trans.set_virtual_path_info("/" + "/".join(vpath_fields[2:]))

            # Let the viewer decide about the structure below this resource.

            self.viewer.respond(trans)
            raise EndOfResponse

        else:

            # Set any restricting item type criteria.

            if self.default_item_type is not None:
                attributes["item-type"] = self.default_item_type

            # Either present the items in a property view or give an error.

            if trans.get_request_method() == "PROPFIND":
                self.prop_viewer.respond(trans)
                raise EndOfResponse
            else:
                trans.set_response_code(405)
                trans.get_response_stream().write("Method not allowed")
                raise EndOfResponse

class ExporterSelectorResource:

    """
    A resource which examines the path information of a request and dispatches
    to the appropriate export resource.
    """

    path_encoding = "utf-8"

    def __init__(self, item_type, collection_exporter, prop_viewer):
        self.item_type = item_type
        self.collection_exporter = collection_exporter
        self.prop_viewer = prop_viewer

    def respond(self, trans):

        """
        Determine how a special collection export location is being accessed and
        dispatch to a collection exporter or a property viewer for that
        location.
        """

        attributes = trans.get_attributes()
        attributes["item-type"] = self.item_type
        attributes["collection-export"] = "true"

        if trans.get_request_method() == "GET":
            self.collection_exporter.respond(trans)
            raise EndOfResponse

        elif trans.get_request_method() == "PROPFIND":
            self.prop_viewer.respond(trans)
            raise EndOfResponse

        # Disallow other methods.

        else:
            trans.set_response_code(405)
            trans.get_response_stream().write("Method not allowed")
            raise EndOfResponse

# vim: tabstop=4 expandtab shiftwidth=4
