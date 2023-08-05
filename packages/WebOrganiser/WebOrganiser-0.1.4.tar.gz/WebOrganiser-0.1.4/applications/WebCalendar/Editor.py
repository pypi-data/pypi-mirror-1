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
from WebCalendar.Common import rdfcalendar_item_types, rdfcalendar_calendar_item_types
import os
import time
import urllib

# Resource classes.

class ItemEditorResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "An event/to-do item editor."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    template_resources = {
        "event" : ("event_template.xhtml", "event_output.xsl"),
        "to-do" : ("to_do_template.xhtml", "to_do_output.xsl"),
        "card" : ("card_template.xhtml", "card_output.xsl"),
        "journal" : ("journal_template.xhtml", "journal_output.xsl")
        }
    init_resources = {
        "event" : ("event_template.xhtml", "event_input.xsl"),
        "to-do" : ("to_do_template.xhtml", "to_do_input.xsl"),
        "card" : ("card_template.xhtml", "card_input.xsl"),
        "journal" : ("journal_template.xhtml", "journal_input.xsl")
        }
    transform_resources = {
        "event" : ["event_prepare.xsl"],
        "event-unprepare" : ["event_unprepare.xsl"],
        "card" : ["card_prepare.xsl"],
        "card-unprepare" : ["card_unprepare.xsl"],
        "event-calendar" : ["event_calendar_mark.xsl"]
        }
    in_page_resources = {
        "event-datetimes" : ("event", "event_datetimes_output.xsl", "datetimes-node"),
        "journal-datetimes" : ("journal", "journal_datetimes_output.xsl", "datetimes-node")
    }
    document_resources = {
        "adr" : "card_adr.xml",
        "label" : "card_label.xml",
        "tel" : "card_tel.xml",
        "translations" : "translations.xml"
    }

    def __init__(self, store):
        self.store = store

    def respond_to_form(self, trans, form):

        """
        Respond to a request having the given transaction 'trans' and the given
        'form' information.
        """

        # Get useful information about the request.

        pvpath = trans.get_processed_virtual_path_info(self.path_encoding)
        parent_path = trans.update_path(pvpath, "")

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

        # If no document can be found, signal failure.

        doc = self.get_document(form, item, item_type)
        if doc is None:
            trans.set_response_code(500)
            trans.get_response_stream().write("Item type not understood")
            raise EndOfResponse

        # Perform any actions.

        parameters = form.get_parameters()
        if parameters.has_key("save"):

            # Add non-user-supplied information.

            self._add_related_to(doc, attributes)
            self._add_dates(doc, item)

            if self.save_document(doc, item, item_type):
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

        if parameters.has_key("find-person"):
            self._remove_suggestions(doc, "/item/*/person-suggestions")
            self._find_suggestions(doc, "/item/*/person-search", "/item/*/person-suggestions")

        # Produce calendars for the start and end of the event.

        dtstart, (dtstart_date, dtstart_time) = self._get_dtelement(doc, "/item/*/dtstart")
        dtend, (dtend_date, dtend_time) = self._get_dtelement(doc, "/item/*/dtend")
        dtstart_month, start_date = self._get_month(doc, "/item/*/dtstart/month")
        dtend_month, end_date = self._get_month(doc, "/item/*/dtend/month")

        # Get the current date and time.

        year_now, month_now, day_now = time.localtime()[:3]
        time_in_day_now = "" # time.strftime("%H%M%S")

        # Since the dtstart and dtend datetimes are removed after navigating
        # away from them in the month navigator, the month start/end values
        # can be derived from dtstart/dtend if they are present, or taken
        # directly from the document if they are not.

        if dtstart_date is not None:
            start_date = (dtstart_date[0], dtstart_date[1])

        if dtend_date is not None:
            end_date = (dtend_date[0], dtend_date[1])

        # Detect the month navigation actions.
        # Remove any datetime set through month navigation - this makes the user set the
        # field in the form, avoiding lost information in a full-page update after
        # in-page updates.

        if parameters.has_key("previous-start"):
            start_date, _tmp = self._previous_month(start_date)
            dtstart_date, dtstart_time = None, None
        elif parameters.has_key("next-start"):
            start_date, end_date = self._next_month(start_date, end_date)
            dtstart_date, dtstart_time = None, None
        elif parameters.has_key("previous-end"):
            end_date, start_date = self._previous_month(end_date, start_date)
            dtend_date, dtend_time = None, None
        elif parameters.has_key("next-end"):
            end_date, _tmp = self._next_month(end_date)
            dtend_date, dtend_time = None, None

        # Where no month navigation values are present, use the current date.

        if start_date is None:
            start_date = (year_now, month_now)

        if end_date is None:
            end_date = (year_now, month_now)

        # Update the datetimes. Here, we remove any existing month data, update
        # the datetime attribute or remove it if month navigation has occurred.

        if dtstart is not None:
            if dtstart_month is not None:
                dtstart_month.parentNode.removeChild(dtstart_month)
            if dtstart_date is not None:
                dtstart.setAttribute("datetime", "%04d%02d%02d%s" % (dtstart_date + (dtstart_time,)))
            elif dtstart.hasAttribute("datetime"):
                dtstart.removeAttribute("datetime")
            XMLCalendar.write_month_to_document(doc, dtstart, start_date[0], start_date[1])

            # Add the current date for informational purposes.

            dtstart.setAttribute("today", "%04d%02d%02d" % (year_now, month_now, day_now))

        if dtend is not None:
            if dtend_month is not None:
                dtend_month.parentNode.removeChild(dtend_month)
            if dtend_date is not None:
                dtend.setAttribute("datetime", "%04d%02d%02d%s" % (dtend_date + (dtend_time,)))
            elif dtend.hasAttribute("datetime"):
                dtend.removeAttribute("datetime")
            XMLCalendar.write_month_to_document(doc, dtend, end_date[0], end_date[1])

            # Add the current date for informational purposes.

            dtend.setAttribute("today", "%04d%02d%02d" % (year_now, month_now, day_now))

        # Process the calendar, adding marked, start and end attributes.

        if dtstart is not None:
            event_calendar_xsl_list = self.prepare_transform("event-calendar")
            doc = self.get_result(event_calendar_xsl_list, doc)

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

        # Get the translations.

        translations_xml = self.prepare_document("translations")
        languages = trans.get_content_languages()
        try:
            language = languages[0]
        except IndexError:
            language = ""
        stylesheet_parameters["locale"] = language

        # Actually send the response.

        self.send_output(trans, [trans_xsl], doc, stylesheet_parameters,
            references={"translations" : translations_xml})

    # Document initialisation and storage methods.

    def get_document(self, form, item, item_type):

        """
        Return the document being edited for the given 'form', 'item' and
        'item_type'.
        """

        documents = form.get_documents()

        # Find an item being edited...

        if documents.has_key("item"):
            doc = documents["item"]

        # Or obtain the item definition.

        elif item_type in rdfcalendar_item_types:
            doc = form.new_instance("item")
            doc_root = doc.xpath("*")[0]

            # Get the definition if we have one.

            if item is not None:
                self.store.fill_element_serialised(doc, doc_root, [item], qualifier=(None, ""))

                # Restructure the serialised form.
                # This moves certain elements inside others and merges person
                # information into the right elements.

                if item_type in rdfcalendar_calendar_item_types:

                    # Get the person definitions.

                    self._insert_cards(doc, doc_root)
                    prepare_xsl_list = self.prepare_transform("event")
                else:
                    prepare_xsl_list = self.prepare_transform("card")

                doc = self.get_result(prepare_xsl_list, doc)
        else:
            doc = None

        return doc

    def save_document(self, doc, item, item_type):

        """
        Save the given document 'doc' using the 'item' and 'item_type'
        information to first process the document before presenting it to the
        data store.
        """

        # Restructure the serialised form, merging fields which have to be
        # combined into single values.

        if item_type == "card":
            unprepare_xsl_list = self.prepare_transform("card-unprepare")
            doc = self.get_result(unprepare_xsl_list, doc)
        elif item_type in ("event", "to-do", "journal"):
            unprepare_xsl_list = self.prepare_transform("event-unprepare")
            doc = self.get_result(unprepare_xsl_list, doc)

        # Remove any existing item.

        if item is not None:
            self.store.remove_item(item)

        # Where no existing item exists, try and find a reasonable identifier.
        # Do not allow items to be saved without a proper item reference.

        elif item_type == "card":
            uriref_values = doc.xpath("/item/*//email/@details")
            if len(uriref_values) > 0:
                uriref_value = uriref_values[0].nodeValue
                if uriref_value:
                    item = self.store.URIRef("MAILTO:" + uriref_value)
                else:
                    return 0
            else:
                return 0

        elif item_type in ("event", "to-do", "journal"):
            summary_values = doc.xpath("/item/*/summary/@details")
            if len(summary_values) > 0:
                summary_value = summary_values[0].nodeValue
                if summary_value:
                    # NOTE: This will not work with various leading characters.
                    # Change the summary into a URL-encoded identifier.
                    item = self.store.get_item_from_identifier(urllib.quote(summary_value))
                    while self.store.has_item(item):
                        summary_value += "'"
                        item = self.store.get_item_from_identifier(urllib.quote(summary_value))
                else:
                    return 0
            else:
                return 0

        # Add a new item.

        self.store.add_item(item, doc)
        return 1

    # Methods adding information for saving.

    def _add_dates(self, doc, item):

        """
        Add date information to the given document 'doc', providing creation
        date information if the specified 'item' is None.
        """

        time_now = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        last_modified_dates = doc.xpath("item/*/last-modified")
        if last_modified_dates:
            last_modified_dates[0].setAttribute("datetime", time_now)
        if item is None:
            created_dates = doc.xpath("item/*/created")
            if created_dates:
                created_dates[0].setAttribute("datetime", time_now)
            dtstamp_dates = doc.xpath("item/*/dtstamp")
            if dtstamp_dates:
                dtstamp_dates[0].setAttribute("datetime", time_now)

    def _add_related_to(self, doc, attributes):

        """
        Add related-to information to the given document 'doc', using the
        'attributes' provided to supply the necessary details.
        """

        # NOTE: To be improved.
        related_tos = doc.xpath("/item/*/related-to")
        if related_tos and (not related_tos[0].hasAttribute("uri") or not related_tos[0].getAttribute("uri")) and \
            attributes.get("filter-type") == "related-to":
            related_to = attributes["filter-item-value"]
            related_tos[0].setAttribute("uri", unicode(self.store.get_item_from_identifier(related_to)))

    # Datetime-related methods.

    def _get_dtelement(self, doc, name_path):
        dtelements = doc.xpath(name_path)
        if dtelements:
            dtelement = dtelements[0]
            if dtelement.hasAttribute("datetime"):
                dtelement_value = dtelement.getAttribute("datetime")
                dtelement_year, dtelement_month, dtelement_day, dtelement_time = \
                    int(dtelement_value[:4]), int(dtelement_value[4:6]), int(dtelement_value[6:8]), dtelement_value[8:]
                return dtelement, ((dtelement_year, dtelement_month, dtelement_day), dtelement_time)
            else:
                return dtelement, (None, None)
        return None, (None, None)

    def _get_month(self, doc, name_path):
        months = doc.xpath(name_path)
        if months:
            month = months[0]
            if month.hasAttribute("year") and month.hasAttribute("number"):
                return month, (int(month.getAttribute("year")), int(month.getAttribute("number")))
            else:
                return month, None
        else:
            return None, None

    def _previous_month(self, date, limit_date=None):
        year, month = date
        if limit_date is not None:
            limit_year, limit_month = limit_date
        month -= 1
        if month == 0:
            month = 12
            year -= 1
        if limit_date is not None and (year, month) < (limit_year, limit_month):
            limit_date = year, month
        return (year, month), limit_date

    def _next_month(self, date, limit_date=None):
        year, month = date
        if limit_date is not None:
            limit_year, limit_month = limit_date
        month += 1
        if month == 13:
            month = 1
            year += 1
        if limit_date is not None and (year, month) > (limit_year, limit_month):
            limit_date = year, month
        return (year, month), limit_date

    # Person initialisation methods.

    def _insert_cards(self, doc, root, element_name="cards"):

        """
        Insert cards for people mentioned in the given document 'doc', under the
        given 'root' using the given 'element_name' as a container for the new
        elements.
        """

        cards = doc.createElement(element_name)
        root.appendChild(cards)
        for person in doc.xpath("//item/*/organizer|//item/*/attendee"):
            # NOTE: The usage of either BNode or URIRef objects requiring the
            # NOTE: given call is likely to be phased out in favour of only
            # NOTE: URIRef objects being used.
            person_id = self.store.get_item_from_reference(person.getAttribute("uri"))
            self.store.fill_element_serialised(doc, cards, [person_id], qualifier=(None, ""))

    # Person searching methods.

    def _find_suggestions(self, doc, value_path, element_container_path, attribute_name="term"):

        """
        Find the element in 'doc' residing on the 'value_path' and ensure the
        presence of elements at 'element_container_path' having the given
        'element_name'.
        """

        value_element = doc.xpath(value_path)[0]
        value = value_element.getAttribute(attribute_name)
        container = doc.xpath(element_container_path)[0]
        self._fill_suggestions(doc, container, value)

    def _remove_suggestions(self, doc, element_container_path):
        container = doc.xpath(element_container_path)[0]
        for element in container.xpath("*"):
            container.removeChild(element)

    def _fill_suggestions(self, doc, root, value):

        """
        In 'doc', within 'root', use the 'value' to query the store, adding
        a new element for each item.
        """

        if value != "":
            suggestion_items = self.store.get_filtered_items([
                (["organizer", "uri"], ("startswith", value)),
                (["attendee", "uri"], ("startswith", value)),
                (["email", "details"], ("startswith", value)),
                (["fn", "details"], ("startswith", value))
                ])
        else:
            suggestion_items = []

        # Add the found values.

        self.store.fill_element_serialised(doc, root, suggestion_items, qualifier=(None, ""))

    def _set_suggestion(self, doc, element, element_container_path, element_name):

        """
        Get a value from 'element', adding within the 'element_container_path'
        an element with the given 'element_name'.
        """

        # Create the new element to hold the suggestion details.

        container = doc.xpath(element_container_path)[0]
        new_element = doc.createElement(element_name)

        # Copy the interesting attributes from the suggestion.

        for attribute_name, suggested_paths in [("uri", "uid/@details"), ("fn", "fn/@details"), ("email", "email/@details")]:
            suggested_value = element.xpath(suggested_paths)[0].nodeValue
            new_element.setAttribute(attribute_name, suggested_value)

        container.appendChild(new_element)

# vim: tabstop=4 expandtab shiftwidth=4
