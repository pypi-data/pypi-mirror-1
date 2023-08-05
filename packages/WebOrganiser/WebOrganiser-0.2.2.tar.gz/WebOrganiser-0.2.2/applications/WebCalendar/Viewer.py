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
import XSLForms.Resources.WebResources
import XSLForms.Utils
from XSLTools import XMLCalendar
from WebCalendar.Exporter import export_items
import os
import time # for default filter information

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
        ppath = trans.get_path_without_info(self.path_encoding) + pvpath

        # Get the items in the form.

        documents = form.get_documents()

        if documents.has_key("items"):
            items = documents["items"]
            items_root = items.xpath("*")[0]

        # Find the date information.

        attributes = trans.get_attributes()
        year = attributes["year"]
        month = attributes["month"]
        day = attributes.get("day")

        # Find the items according to the attributes.

        found_items = self.store.get_items_using_attributes(attributes)

        # Check for download actions.

        parameters = form.get_parameters()
        if parameters.has_key("download-all"):
            trans.set_content_type(ContentType("text/calendar", self.encoding))
            stream = trans.get_response_stream()
            export_items(found_items, self.store, stream)
            raise EndOfResponse

        elif parameters.has_key("new"):
            new_type = items.xpath("items/new-type/@value")[0].nodeValue
            new_path = trans.update_path(ppath, "../%s/new/" % new_type)
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

        # Add item types.

        add_item_types(items, items_root, self.store)

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
        stylesheet_parameters["root"] = attributes["root"]

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
        ppath = trans.get_path_without_info(self.path_encoding) + pvpath

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

        found_items = self.store.get_items_using_attributes(attributes)

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

        elif parameters.has_key("new"):
            new_type = items.xpath("items/new-type/@value")[0].nodeValue
            new_path = trans.update_path(ppath, "../%s/new/" % new_type)
            trans.redirect(trans.encode_path(new_path, self.path_encoding))
            # Response ended!

        # Produce a new document.

        items = form.new_instance("items")
        items_root = items.xpath("*")[0]

        # Add any filtering details.
        # These involve additional components on the path which affect URLs
        # stated in the output.

        set_filter_attributes(items_root, attributes)

        # Add item types.

        add_item_types(items, items_root, self.store)

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
        stylesheet_parameters["root"] = attributes["root"]

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

    def __init__(self, store):
        self.store = store

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        # Get the processed path details and a version suitable for output.

        pvpath = trans.get_processed_virtual_path_info(self.path_encoding)
        ppath = trans.get_path_without_info(self.path_encoding) + pvpath
        encoded_pvpath = "/".join([trans.encode_path(part, self.path_encoding) for part in pvpath.split("/")])
        encoded_ppath = trans.get_path_without_info(self.path_encoding) + encoded_pvpath

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

            # Set special attributes in order to indicate different kinds of
            # resources in the container.

            if attributes.has_key("filter-type") and not attributes.has_key("filter-item-value"):
                items_root.setAttribute("items-are-containers", "yes")
            else:
                items_root.setAttribute("items-are-containers", "no")

            # Support collections represented by file-like resources.

            if attributes.has_key("collection-export"):
                items_root.setAttribute("leaf", "yes")
                items_root.setAttribute("collection-export", "yes")
                found_items = []
            else:
                # Fix the path information, if necessary.

                if not encoded_pvpath.endswith("/"):
                    encoded_pvpath += "/"

                found_items = self.store.get_items_using_attributes(attributes)
                set_filter_attributes(items_root, attributes)

        # Produce the triple information.

        table = items.createElement("table")
        items_root.appendChild(table)
        self.store.fill_element(items, table, found_items)

        # Start the response.

        trans.set_content_type(ContentType("application/xml", self.encoding))

        # Define the stylesheet parameters.

        stylesheet_parameters = {
            "path" : encoded_ppath
            }
        stylesheet_parameters["root"] = attributes["root"]

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

        attributes = trans.get_attributes()

        # Get the processed path details and a version suitable for output.

        pvpath = trans.get_processed_virtual_path_info(self.path_encoding)
        ppath = trans.get_path_without_info(self.path_encoding) + pvpath
        encoded_pvpath = "/".join([trans.encode_path(part, self.path_encoding) for part in pvpath.split("/")])
        encoded_ppath = trans.get_path_without_info(self.path_encoding) + encoded_pvpath

        # Invent a document based on the resources.

        doc = form.new_document(self.default_document)
        top = doc.xpath("*")[0]
        for directory in self.get_directories(trans, pvpath):
            e = doc.createElement("directory")
            e.setAttribute("name", directory)
            top.appendChild(e)
        for file in self.get_files(trans, pvpath):
            e = doc.createElement("file")
            e.setAttribute("name", file)
            top.appendChild(e)

        # Start the response.

        trans.set_content_type(ContentType("application/xml", self.encoding))

        # Define the stylesheet parameters.

        stylesheet_parameters = {
            "path" : encoded_ppath
            }
        stylesheet_parameters["root"] = attributes["root"]

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

    def get_directories(self, trans, pvpath):
        return map(str, range(1, 13))

    def get_files(self, trans, pvpath):
        return []

class RootViewerResource(SimpleViewerResource):

    "A root resource information viewer."

    template_resources = {
        "root" : ("root_template.xml", "root_output.xsl")
        }
    default_document = "root"

    def __init__(self, store):
        self.store = store

    def get_directories(self, trans, pvpath):
        d = ["all"]
        d += self.store.get_supported_item_types()
        #if pvpath == "/":
        #    d.append("calendar")
        #    d.append("card")
        if not trans.get_attributes().has_key("filter-type"):
            d.append("related-to")
            d.append("person")
        return d

    def get_files(self, trans, pvpath):
        return ["all.ics", "event.ics", "to-do.ics", "free-busy.ics"]

# Common functions.

def add_item_types(items, items_root, store):

    """
    Add the item types to the 'items' document, under 'items_root', using
    information from the 'store'.
    """

    new_type = items.createElement("new-type")
    items_root.appendChild(new_type)
    item_types = items.createElement("item-types")
    items_root.appendChild(item_types)

    item_type = items.createElement("item-type")
    item_type.setAttribute("value", "all")
    item_types.appendChild(item_type)

    supported_item_types = store.get_supported_item_types()
    supported_item_types.sort()

    for item_type_label in supported_item_types:
        new_type_enum = items.createElement("new-type-enum")
        new_type_enum.setAttribute("value", item_type_label)
        new_type.appendChild(new_type_enum)
        item_type = items.createElement("item-type")
        item_type.setAttribute("value", item_type_label)
        item_types.appendChild(item_type)

def set_filter_attributes(element, attributes):

    "In the given 'element', set filter information from the 'attributes'."

    if attributes.has_key("filter-type"):
        element.setAttribute("filter-type", attributes["filter-type"])
    if attributes.has_key("item-type"):
        element.setAttribute("item-type", attributes["item-type"])

    if attributes.has_key("year"):
        element.setAttribute("year", str(attributes["year"]))
    if attributes.has_key("month"):
        element.setAttribute("month", str(attributes["month"]))

    year_now, month_now = time.gmtime()[0:2]
    element.setAttribute("year-now", str(year_now))
    element.setAttribute("month-now", str(month_now))

    if attributes.has_key("filter-item-value"):
        element.setAttribute("filter-item-value", attributes["filter-item-value"])
        if attributes.get("filter-type") == "related-to":
            element.setAttribute("related-to", attributes["filter-item-value"])
            element.setAttribute("filtered", "yes")
        elif attributes.get("filter-type") == "person":
            element.setAttribute("person", attributes["filter-item-value"])
            element.setAttribute("filtered", "yes")

# vim: tabstop=4 expandtab shiftwidth=4
