#!/usr/bin/env python

"""
Editor classes.

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
import os
import time
import calendar

# Resource classes.

class ItemEditorResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "An event/to-do item editor."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    template_resources = {
        "event" : ("event_template.xhtml", "event_output.xsl"),
        "to-do" : ("to_do_template.xhtml", "to_do_output.xsl"),
        "card" : ("card_template.xhtml", "card_output.xsl")
        }
    init_resources = {
        "event" : ("event_template.xhtml", "event_input.xsl"),
        "to-do" : ("to_do_template.xhtml", "to_do_input.xsl"),
        "card" : ("card_template.xhtml", "card_input.xsl")
        }
    transform_resources = {
        "event" : ["event_prepare.xsl"],
        "event-unprepare" : ["event_unprepare.xsl"],
        "card" : ["card_prepare.xsl"],
        "card-unprepare" : ["card_unprepare.xsl"]
        }
    in_page_resources = {
        "datetimes" : ("event", "event_datetimes_output.xsl", "datetimes-node")
    }
    document_resources = {
        "adr" : "card_adr.xml",
        "label" : "card_label.xml",
        "tel" : "card_tel.xml"
    }

    def __init__(self, store):
        self.store = store

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        # Determine which item is being edited.
        # The item type can be advisory since this may be a new item where we
        # cannot test the item type against something in the store.

        attributes = trans.get_attributes()
        item_type = attributes["item-type"]
        item_value = attributes["item-value"]

        # Where a new item is requested, use None for the item.

        if item_value == "new":
            item = None
        else:
            item = self.store.get_item_from_identifier(item_value)

        # Get useful information about the request.

        pvpath = trans.get_processed_virtual_path_info(self.path_encoding)
        parent_path = trans.update_path(pvpath, "")
        documents = form.get_documents()

        # Find an item being edited...

        if documents.has_key("item"):
            doc = documents["item"]

        # Or obtain the item definition.

        elif item_type in ("event", "to-do", "card"):
            doc = form.new_instance("item")
            doc_root = doc.xpath("*")[0]

            # Get the definition if we have one.

            if item is not None:
                self.store.fill_element_serialised(doc, doc_root, [item])

                # Restructure the serialised form.
                # This just fixes the prefixes in the serialised document and moves
                # certain elements inside others.

                if item_type in ("event", "to-do"):
                    prepare_xsl_list = self.prepare_transform("event")
                else:
                    prepare_xsl_list = self.prepare_transform("card")

                doc = self.get_result(prepare_xsl_list, doc)

        # Otherwise, signal failure.

        else:
            trans.set_response_code(500)
            trans.get_response_stream().write("Item type not understood")
            raise EndOfResponse

        # Useful information.

        time_now = time.strftime("%Y%m%dT%H%M%S")
        last_modified_dates = doc.xpath("item/*/last-modified")
        if last_modified_dates:
            last_modified_dates[0].setAttribute("datetime", time_now)

        # Perform any actions.

        parameters = form.get_parameters()
        if parameters.has_key("save"):

            # Restructure the serialised form, merging fields which have to be
            # combined into single values.

            if item_type == "card":
                unprepare_xsl_list = self.prepare_transform("card-unprepare")
                doc = self.get_result(unprepare_xsl_list, doc)
            elif item_type in ("event", "to-do"):
                unprepare_xsl_list = self.prepare_transform("event-unprepare")
                doc = self.get_result(unprepare_xsl_list, doc)

            # Remove any existing item.

            if item is not None:
                self.store.remove_item(item)

            # Add a new item - this should assign a new identifier for the item.

            self.store.add_item(item, doc)
            trans.redirect(trans.encode_path(parent_path, self.path_encoding))
            # Response ended!

        elif parameters.has_key("cancel"):
            trans.redirect(trans.encode_path(parent_path, self.path_encoding))
            # Response ended!

        # (Card selectors)
        # These need to be present before initialisation in order that the added
        # elements are present and are each given any multiple-choice options
        # that are introduced in the initialisation process.

        selectors = form.get_selectors()
        XSLForms.Utils.add_elements(selectors.get("add-n-field"), "field", "fields", "n")
        XSLForms.Utils.add_elements(selectors.get("add-adr-field"), "field", "fields")
        XSLForms.Utils.add_elements(selectors.get("add-adr"), "adr", "addresses")
        XSLForms.Utils.add_elements(selectors.get("add-tel"), "tel", "telephones")
        XSLForms.Utils.add_elements(selectors.get("add-label"), "label", "labels")

        # (General selectors)

        XSLForms.Utils.remove_elements(selectors.get("remove"))

        # Ensure the structure of the document.

        init_xsl = self.prepare_initialiser(item_type)

        # Perform the initialisation.

        if item_type == "card":

            # Produce appropriate card enumerations.

            doc = self.get_result([init_xsl], doc, references={
                "adr" : self.prepare_document("adr"),
                "label" : self.prepare_document("label"),
                "tel" : self.prepare_document("tel")
                })
        else:
            doc = self.get_result([init_xsl], doc)

        # Perform any requested additions and removals.

        form.set_document("item", doc)
        selectors = form.get_selectors()

        # (Event and to-do selectors)

        for organizer in selectors.get("select-organizer", []):
            self._set_suggestion(doc, organizer, "/item/*/organizers", "organizer")
        for attendee in selectors.get("select-attendee", []):
            self._set_suggestion(doc, attendee, "/item/*/attendees", "attendee")

        # Move things around into newly-prepared sections of the document.
        # Insert the search results.

        if parameters.has_key("find-organizer"):
            self._remove_suggestions(doc, "/item/*/organizer-suggestions")
            self._find_suggestions(doc, "/item/*/organizer-search", "/item/*/organizer-suggestions", "organizer-suggestion")
        if parameters.has_key("find-attendee"):
            self._remove_suggestions(doc, "/item/*/attendee-suggestions")
            self._find_suggestions(doc, "/item/*/attendee-search", "/item/*/attendee-suggestions", "attendee-suggestion")

        # Produce calendars for the start and end of the event.

        dtstart, (dtstart_date, dtstart_time) = self._get_dtelement(doc, "dtstart")
        dtend, (dtend_date, dtend_time) = self._get_dtelement(doc, "dtend")

        # Where no dtstart or dtend exists, use the current month.

        year_now, month_now, day_now = time.localtime()[:3]
        time_in_day_now = time.strftime("%H%M%S")

        if dtstart_time is None:
            dtstart_date = (year_now, month_now, day_now)
            dtstart_time = time_in_day_now
        if dtend_time is None:
            dtend_date = (year_now, month_now, day_now)
            dtend_time = time_in_day_now

        # Detect the month navigation actions.

        if parameters.has_key("previous-start"):
            dtstart_date = self._previous_month(dtstart_date)
        elif parameters.has_key("next-start"):
            dtstart_date = self._next_month(dtstart_date, dtend_date)
        elif parameters.has_key("previous-end"):
            dtend_date = self._previous_month(dtend_date, dtstart_date)
        elif parameters.has_key("next-end"):
            dtend_date = self._next_month(dtend_date)

        # Update the datetimes.

        if dtstart is not None:
            dtstart.setAttribute("datetime", "%04d%02d%02d%s" % (dtstart_date + (dtstart_time,)))
            XMLCalendar.write_month_to_document(doc, dtstart, dtstart_date[0], dtstart_date[1])
        if dtend is not None:
            dtend.setAttribute("datetime", "%04d%02d%02d%s" % (dtend_date + (dtend_time,)))
            XMLCalendar.write_month_to_document(doc, dtend, dtend_date[0], dtend_date[1])

        # Start the response.

        trans.set_content_type(ContentType("application/xhtml+xml", self.encoding))

        # Complete the response.

        in_page_resource = self.get_in_page_resource(trans)

        if in_page_resource in self.in_page_resources.keys():
            trans_xsl = self.prepare_fragment(in_page_resource)
            stylesheet_parameters = self.prepare_parameters(parameters)
        else:
            trans_xsl = self.prepare_output(item_type)
            stylesheet_parameters = {}
        self.send_output(trans, [trans_xsl], doc, stylesheet_parameters)

    # Datetime-related methods.

    def _get_dtelement(self, doc, name):
        dtelements = doc.xpath("item/*/" + name)
        if dtelements:
            dtelement = dtelements[0]
            if dtelement.hasAttribute("datetime"):
                dtelement_value = dtelement.getAttribute("datetime")
                dtelement_year, dtelement_month, dtelement_day, dtelement_time = \
                    int(dtelement_value[:4]), int(dtelement_value[4:6]), int(dtelement_value[6:8]), dtelement_value[8:]
            else:
                dtelement_year, dtelement_month, dtelement_day, dtelement_time = \
                    (None, None, None, None)
            return dtelement, ((dtelement_year, dtelement_month, dtelement_day), dtelement_time)
        return None, (None, None)

    def _previous_month(self, date, limit_date=None):
        year, month, day = date
        if limit_date is not None:
            limit_year, limit_month, limit_day = limit_date
        if limit_date is None or (year, month) > (limit_year, limit_month):
            month -= 1
            if month == 0:
                month = 12
                year -= 1
            if limit_date is not None and (year, month) == (limit_year, limit_month) and day < limit_day:
                day = limit_day
            day1, ndays = calendar.monthrange(year, month)
            return year, month, min(day, ndays)
        return year, month, day

    def _next_month(self, date, limit_date=None):
        year, month, day = date
        if limit_date is not None:
            limit_year, limit_month, limit_day = limit_date
        if limit_date is None or (year, month) < (limit_year, limit_month):
            month += 1
            if month == 13:
                month = 1
                year += 1
            if limit_date is not None and (year, month) == (limit_year, limit_month) and day > limit_day:
                day = limit_day
            day1, ndays = calendar.monthrange(year, month)
            return year, month, min(day, ndays)
        return year, month, day

    def _find_suggestions(self, doc, value_path, element_container_path, element_name, attribute_name="uri"):

        """
        Find the element in 'doc' residing on the 'value_path' and ensure the
        presence of elements at 'element_container_path' having the given
        'element_name'.
        """

        value_element = doc.xpath(value_path)[0]
        value = value_element.getAttribute(attribute_name)
        container = doc.xpath(element_container_path)[0]
        self._fill_suggestions(doc, container, value, element_name)

    def _remove_suggestions(self, doc, element_container_path):
        container = doc.xpath(element_container_path)[0]
        for element in container.xpath("*"):
            container.removeChild(element)

    def _fill_suggestions(self, doc, root, value, element_name, attribute_name="uri"):

        """
        In 'doc', within 'root', use the 'value' to query the store, adding
        elements with the given 'element_name'.
        """

        if value != "":
            suggestion_values = self.store.get_filtered_values([
                (["uri"], [("startswith", value)]),
                (["email", "details"], [("startswith", value)])
                ])
        else:
            suggestion_values = []

        # Add the found values.

        for suggestion_value in suggestion_values:
            suggestion = doc.createElement(element_name)
            suggestion.setAttribute(attribute_name, suggestion_value)
            root.appendChild(suggestion)

    def _set_suggestion(self, doc, element, element_container_path, element_name, attribute_name="uri"):

        """
        Get a value from 'element', adding within the 'element_container_path'
        an element with the given 'element_name'.
        """

        suggested_value = element.getAttribute(attribute_name)
        container = doc.xpath(element_container_path)[0]
        new_element = doc.createElement(element_name)
        new_element.setAttribute(attribute_name, suggested_value)
        container.appendChild(new_element)

# vim: tabstop=4 expandtab shiftwidth=4
