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
import os
import datetime # for querying

# Standard Web-oriented resource classes.

class IndexViewerResource(XSLForms.Resources.WebResources.XSLFormsResource):

    "A portal index page viewer."

    resource_dir = os.path.join(os.path.split(__file__)[0], "Resources")
    encoding = "utf-8"
    path_encoding = "utf-8"
    template_resources = {
        "index" : ("index_template.xhtml", "index_output.xsl")
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

        # Filter according to certain criteria.

        if not getattr(self.store.store, "supports_querying", 0):
            trans.set_content_type(ContentType("text/plain"))
            trans.set_response_code(500)
            trans.get_response_stream.write("Portal data store does not support querying.")
            raise EndOfResponse

        # Produce a new document.

        site = form.new_instance("site")
        site_root = site.xpath("*")[0]

        # Determine a date range.

        #date_from = datetime.datetime.utcnow()
        date_from = datetime.datetime(2006, 1, 1)
        #date_to = date_from + datetime.timedelta(days=8)
        date_to = date_from + datetime.timedelta(days=90)

        # We want to find nodes which state datetimes according to the above
        # date information.

        sqlstore = self.store.store
        dates = sqlstore.Expression("_ >= ? and _ < ?", [
            date_from.strftime("%Y%m%d"), date_to.strftime("%Y%m%d")
            ])

        # NOTE: Use attributes to produce [[p1, p2], [q1, q2], [r1, r2]].
        # NOTE: Then, use [p1, q1, r1], [p2, q2, r2] in the query.

        date_types = []
        date_types += self.store.get_urirefs_for_property_type("dtstart")
        date_types += self.store.get_urirefs_for_property_type("dtend")
        date_types += self.store.get_urirefs_for_property_type("created")

        # Now, add sections to the document for each interesting item type.
        # NOTE: Replace with a generic list of item types.

        for section_name, item_type_name in [("events", "event"), ("tasks", "to-do"), ("cards", "card"), ("journals", "journal"), ("e-mails", "e-mail")]:
            subjects = sqlstore.subjects(self.store.TYPE, self.store.get_urirefs_for_item_type(item_type_name)[0])

            found_items = []
            for tuple in sqlstore.tuples((subjects, date_types, self.store.get_urirefs_for_property_type("datetime"), dates), ordering="asc"):
                if tuple[0] not in found_items:
                    found_items.append(tuple[0])

            # Produce the item section.

            section = site.createElement(section_name)
            site_root.appendChild(section)
            self.store.fill_element(site, section, found_items)

        # Start the response.

        trans.set_content_type(ContentType("application/xhtml+xml", self.encoding))

        # Define the stylesheet parameters.

        stylesheet_parameters = {}

        # Ensure that an output stylesheet exists.
        # Use the list template.

        trans_xsl = self.prepare_output("index")

        # Get the translations.

        translations_xml = self.prepare_document("translations")
        languages = trans.get_content_languages()
        try:
            language = languages[0]
        except IndexError:
            language = ""
        stylesheet_parameters["locale"] = language

        # Complete the response.

        self.send_output(trans, [trans_xsl], site, stylesheet_parameters,
            references={"translations" : translations_xml})

# vim: tabstop=4 expandtab shiftwidth=4
