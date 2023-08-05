#!/usr/bin/env python

"""
Viewer classes.

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
from WebCalendar.Exporter import export_items
import XSLForms.Resources.WebResources
import XSLForms.Utils
from XSLTools import XMLCalendar
import os

# Standard Web-oriented resource classes.

class CalendarViewerResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A calendar viewer."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    path_encoding = "utf-8"
    template_resources = {
        "items_calendar" : ("items_calendar_template.xhtml", "items_calendar_output.xsl")
        }
    transform_resources = {
        "items_calendar_sort" : ["items_calendar_sort.xsl"]
        }
    document_resources = {
        "translations" : "translations.xml"
        }

    # View configuration.

    default_item_types = ["event", "to-do", "card", "message"]

    def __init__(self, store):
        self.store = store

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        # Get paths, specifically the parent, since this will be used to
        # redirect to new resource editors.

        pvpath = trans.get_processed_virtual_path_info(self.path_encoding)

        # Find the date information.

        attributes = trans.get_attributes()
        year = attributes["year"]
        month = attributes["month"]
        day = attributes.get("day")

        # Find the items according to the attributes.

        found_items = self.store.get_items_using_attributes(attributes, self.default_item_types)

        # Check for download actions.

        parameters = form.get_parameters()
        if parameters.has_key("download-all"):
            trans.set_content_type(ContentType("text/calendar", self.encoding))
            stream = trans.get_response_stream()
            export_items(found_items, self.store, stream)
            raise EndOfResponse

        elif parameters.has_key("new-event"):
            if attributes.has_key("filter-type"):
                new_path = trans.update_path(pvpath, "../../event/new/")
            else:
                new_path = trans.update_path(pvpath, "../event/new/")
            trans.redirect(trans.encode_path(new_path, self.path_encoding))
            # Response ended!

        elif parameters.has_key("new-to-do"):
            if attributes.has_key("filter-type"):
                new_path = trans.update_path(pvpath, "../../to-do/new/")
            else:
                new_path = trans.update_path(pvpath, "../to-do/new/")
            trans.redirect(trans.encode_path(new_path, self.path_encoding))
            # Response ended!

        elif parameters.has_key("new-card"):
            if attributes.has_key("filter-type"):
                new_path = trans.update_path(pvpath, "../../card/new/")
            else:
                new_path = trans.update_path(pvpath, "../card/new/")
            trans.redirect(trans.encode_path(new_path, self.path_encoding))
            # Response ended!

        # Produce a new document.

        items = form.new_instance("items")
        items_root = items.xpath("*")[0]

        # Add any filtering details.
        # These involve additional components on the path which affect URLs
        # stated in the output.

        set_filter_attributes(items_root, attributes)

        # Produce the triple information.

        table = items.createElement("table")
        items_root.appendChild(table)

        # Add any filtering attributes.

        self.store.fill_element(items, table, found_items)

        # Start the response.

        trans.set_content_type(ContentType("application/xhtml+xml", self.encoding))

        # Define the stylesheet parameters.

        stylesheet_parameters = {}

        # Ensure that an output stylesheet exists.
        # Produce a calendar.

        month = XMLCalendar.write_month_to_document(items, items.childNodes[-1], year, month)

        # Place the items in the calendar.

        items_calendar_sort_xsl = self.prepare_transform("items_calendar_sort")
        items = self.get_result(items_calendar_sort_xsl, items)

        # Use the calendar template.

        trans_xsl = self.prepare_output("items_calendar")

        # Get the translations.

        translations_xml = self.prepare_document("translations")
        languages = trans.get_content_languages()
        try:
            language = languages[0]
        except IndexError:
            language = ""
        stylesheet_parameters["locale"] = language

        # Complete the response.

        self.send_output(trans, [trans_xsl], items, stylesheet_parameters,
            references={"translations" : translations_xml})

class ListViewerResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "An item list viewer."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    path_encoding = "utf-8"
    template_resources = {
        "items" : ("items_template.xhtml", "items_output.xsl")
        }
    transform_resources = {
        "items_sort" : ["items_sort.xsl"]
        }
    document_resources = {
        "translations" : "translations.xml"
        }

    # View configuration.

    default_item_types = ["event", "to-do", "card", "message"]

    def __init__(self, store):
        self.store = store

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        # Get paths, specifically the parent, since this will be used to
        # redirect to new resource editors.

        pvpath = trans.get_processed_virtual_path_info(self.path_encoding)

        # Get the items in the form.

        documents = form.get_documents()

        if documents.has_key("items"):
            items = documents["items"]
            items_root = items.xpath("*")[0]

        # Get other settings.

        fields = trans.get_fields_from_path(self.path_encoding)
        attributes = trans.get_attributes()

        # Initialise certain settings.

        sort_by = []
        sort_order = []
        selected_items = []

        # Find selected elements.

        selectors = form.get_selectors()
        if selectors.has_key("item"):
            for item in selectors["item"]:
                # Convert item value identifiers to actual items.
                item_value = self.store.get_item_from_identifier(item.getAttribute("item-value"))
                selected_items.append(item_value)
        else:
            if fields.has_key("sort-by"):
                sort_by = fields["sort-by"]
                del fields["sort-by"]
            if fields.has_key("sort-order"):
                sort_order = fields["sort-order"]
                del fields["sort-order"]

        # Filter according to supplied criteria.

        found_items = self.store.get_items_using_attributes(attributes, self.default_item_types)

        # Check for download actions or editing actions.

        parameters = form.get_parameters()

        if parameters.has_key("download-all"):
            trans.set_content_type(ContentType("text/calendar", self.encoding))
            stream = trans.get_response_stream()
            export_items(found_items, self.store, stream)
            raise EndOfResponse

        elif parameters.has_key("download"):
            trans.set_content_type(ContentType("text/calendar", self.encoding))
            stream = trans.get_response_stream()
            export_items(selected_items, self.store, stream)
            raise EndOfResponse

        elif parameters.has_key("new-event"):
            if attributes.has_key("filter-type"):
                new_path = trans.update_path(pvpath, "../../event/new/")
            else:
                new_path = trans.update_path(pvpath, "../event/new/")
            trans.redirect(trans.encode_path(new_path, self.path_encoding))
            # Response ended!

        elif parameters.has_key("new-to-do"):
            if attributes.has_key("filter-type"):
                new_path = trans.update_path(pvpath, "../../to-do/new/")
            else:
                new_path = trans.update_path(pvpath, "../to-do/new/")
            trans.redirect(trans.encode_path(new_path, self.path_encoding))
            # Response ended!

        elif parameters.has_key("new-card"):
            if attributes.has_key("filter-type"):
                new_path = trans.update_path(pvpath, "../../card/new/")
            else:
                new_path = trans.update_path(pvpath, "../card/new/")
            trans.redirect(trans.encode_path(new_path, self.path_encoding))
            # Response ended!

        # Produce a new document.

        items = form.new_instance("items")
        items_root = items.xpath("*")[0]

        # Add any filtering details.
        # These involve additional components on the path which affect URLs
        # stated in the output.

        set_filter_attributes(items_root, attributes)

        # Produce the triple information.

        table = items.createElement("table")
        items_root.appendChild(table)
        self.store.fill_element(items, table, found_items)

        # Perform sorting.

        if sort_by != []:
            items_sort_xsl = self.prepare_transform("items_sort")
            sort_by.reverse()
            for sort_field, sort_field_order in map(None, sort_by, sort_order):
                items = self.get_result(items_sort_xsl, items,
                    stylesheet_parameters={"sort-by" : sort_field, "sort-order" : sort_field_order or "ascending"})

        # Start the response.

        trans.set_content_type(ContentType("application/xhtml+xml", self.encoding))

        # Define the stylesheet parameters.

        stylesheet_parameters = {}

        # Ensure that an output stylesheet exists.
        # Use the list template.

        trans_xsl = self.prepare_output("items")

        # Get the translations.

        translations_xml = self.prepare_document("translations")
        languages = trans.get_content_languages()
        try:
            language = languages[0]
        except IndexError:
            language = ""
        stylesheet_parameters["locale"] = language

        # Complete the response.

        self.send_output(trans, [trans_xsl], items, stylesheet_parameters,
            references={"translations" : translations_xml})

# WebDAV-oriented resources.

class PropertyViewerResource(XSLForms.Resources.WebResources.XSLFormsResource):

    """
    A property information viewer for items stored in the data store, providing
    detailed information about each item.
    """

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    template_resources = {
        "items" : ("items_properties_template.xml", "items_properties_output.xsl")
        }

    # View configuration.

    default_item_types = ["event", "to-do", "card", "message"]

    def __init__(self, store):
        self.store = store

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        # Get the processed path details and a version suitable for output.

        pvpath = trans.get_processed_virtual_path_info(self.path_encoding)
        encoded_pvpath = "/".join([trans.encode_path(part, self.path_encoding) for part in pvpath.split("/")])

        # Obtain information relevant to the item search.

        attributes = trans.get_attributes()

        # Produce a new document.

        items = form.new_instance("items")
        items_root = items.xpath("*")[0]

        # Either get selected items.
        # This produces a specific WebDAV property view for a file-like resource.

        if attributes.has_key("item-value"):

            # Convert item value identifiers to actual items.

            item_value = attributes["item-value"]
            found_items = self.store.get_selected_items([item_value])

            # Set a special attribute which indicates that a leaf (not a
            # container) is being described.

            items_root.setAttribute("leaf", "yes")

        # Or filter according to supplied criteria.
        # This either produces a WebDAV view for a file-like resource or a view
        # for a directory-like resource.

        else:

            found_items = self.store.get_items_using_attributes(attributes, self.default_item_types)
            set_filter_attributes(items_root, attributes)

            # Set special attributes in order to indicate different kinds of
            # resources in the container.

            if attributes.has_key("filter-type") and not attributes.has_key("filter-item-value"):
                items_root.setAttribute("items-are-containers", "yes")
            else:
                items_root.setAttribute("items-are-containers", "no")

            # Support collections represented by file-like resources.

            if attributes.has_key("collection-export"):
                items_root.setAttribute("leaf", "yes")
            else:
                # Fix the path information, if necessary.

                if not encoded_pvpath.endswith("/"):
                    encoded_pvpath += "/"

        # Produce the triple information.

        table = items.createElement("table")
        items_root.appendChild(table)
        self.store.fill_element(items, table, found_items)

        # Start the response.

        trans.set_content_type(ContentType("application/xml", self.encoding))

        # Define the stylesheet parameters.

        stylesheet_parameters = {
            "path" : trans.get_path_without_info() + encoded_pvpath
            }

        # Ensure that an output stylesheet exists.
        # Use the list template.

        trans_xsl = self.prepare_output("items")

        # Complete the response.

        self.send_output(trans, [trans_xsl], items, stylesheet_parameters)

class SimpleViewerResource(XSLForms.Resources.WebResources.XSLFormsResource):

    """
    A simple information viewer providing elementary information about file and
    directory objects with little additional detail.
    """

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        # Get the processed path details and a version suitable for output.

        pvpath = trans.get_processed_virtual_path_info(self.path_encoding)
        encoded_pvpath = "/".join([trans.encode_path(part, self.path_encoding) for part in pvpath.split("/")])

        # Invent a document based on the resources.

        doc = form.new_document(self.default_document)
        top = doc.xpath("*")[0]
        for directory in self.get_directories(pvpath):
            e = doc.createElement("directory")
            e.setAttribute("name", directory)
            top.appendChild(e)
        for file in self.get_files(pvpath):
            e = doc.createElement("file")
            e.setAttribute("name", file)
            top.appendChild(e)

        # Start the response.

        trans.set_content_type(ContentType("application/xml", self.encoding))

        # Define the stylesheet parameters.

        stylesheet_parameters = {
            "path" : trans.get_path_without_info() + encoded_pvpath
            }

        # Ensure that an output stylesheet exists.

        trans_xsl = self.prepare_output(self.default_document)

        # Complete the response.

        self.send_output(trans, [trans_xsl], doc, stylesheet_parameters)

class MonthViewerResource(SimpleViewerResource):

    "A month information viewer."

    template_resources = {
        "months" : ("months_template.xml", "months_output.xsl")
        }
    default_document = "months"

    def get_directories(self, pvpath):
        return map(str, range(1, 13))

    def get_files(self, pvpath):
        return []

class RootViewerResource(SimpleViewerResource):

    "A root resource information viewer."

    template_resources = {
        "root" : ("root_template.xml", "root_output.xsl")
        }
    default_document = "root"

    def get_directories(self, pvpath):
        d = ["all", "event", "message", "person", "related-to", "to-do"]
        if pvpath == "/":
            d.append("calendar")
            d.append("card")
        return d

    def get_files(self, pvpath):
        return ["all.ics", "event.ics", "to-do.ics"]

# Common functions.

def set_filter_attributes(element, attributes):

    "In the given 'element', set filter information from the 'attributes'."

    if attributes.has_key("filter-type"):
        element.setAttribute("filter-type", attributes["filter-type"])
    elif attributes.has_key("item-type"):
        element.setAttribute("filter-type", attributes["item-type"])
    else:
        element.setAttribute("filter-type", "all")

    if attributes.has_key("filter-item-value"):
        if attributes.get("filter-type") == "related-to":
            element.setAttribute("related-to", attributes["filter-item-value"])
            element.setAttribute("filtered", "yes")
        elif attributes.get("filter-type") == "person":
            element.setAttribute("person", attributes["filter-item-value"])
            element.setAttribute("filtered", "yes")

# vim: tabstop=4 expandtab shiftwidth=4
