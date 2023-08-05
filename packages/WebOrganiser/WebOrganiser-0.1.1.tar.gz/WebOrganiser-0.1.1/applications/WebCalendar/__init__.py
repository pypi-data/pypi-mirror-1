#!/usr/bin/env python

"""
A Web calendar application.

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

__version__ = "0.1.1"

import os

# Site map imports.

from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.Static import DirectoryResource
from WebCalendar.Viewer import *
from WebCalendar.Selector import *
from WebCalendar.Editor import *
from WebCalendar.Exporter import *
from WebCalendar.Importer import *

# Site map initialisation.

def get_site(store):

    "Return a simple Web site resource for the given 'store'."

    # Get the main resources and the directory used by the application.

    list_viewer_resource = ListViewerResource(store)
    calendar_viewer_resource = CalendarViewerResource(store)
    prop_viewer_resource = PropertyViewerResource(store)
    editor_resource = ItemEditorResource(store)
    item_importer_resource = ItemImporterResource(store)
    item_exporter_resource = ItemExporterResource(store)
    collection_exporter_resource = CollectionExporterResource(store)

    # Set up file serving and some directory indexes.

    directory = os.path.join(os.path.split(__file__)[0], "Resources")
    styles_dir = DirectoryResource(os.path.join(directory, "styles"), {"css" : "text/css"})
    scripts_dir = DirectoryResource(os.path.join(directory, "scripts"), {"js" : "text/javascript"})
    webdav_root = RootViewerResource()
    webdav_months = MonthViewerResource()

    # Here's what the site looks like:

    """
    --> date_choices -------------> item_choices ---------------------> view_choices --> ItemSelectorResource
        |                        |  | | | |                        | |  |
        | /date                  |  | | | | /<type>                | |  | /
        |                        |  | | | |                        | |  |
        -> DateSelectorResource --  | | | -> TypeSelectorResource -- |  -> ViewSelectorResource
                                    | | |                            |
                                    | | | /<filter>                  |
                                    | | |                            |
                                    | | -> FilterSelectorResource ----
                                    | |  
                                    | | /<filename>
                                    | |
                                    | -> ExporterSelectorResource
                                    |
                                    | /
                                    |
                                    -> TopSelectorResource
    """

    # Make a simple Web site.

    view_choices = MapResource({
        "styles" : styles_dir,
        "scripts" : scripts_dir,
        "" : ViewSelectorResource(list_viewer_resource, calendar_viewer_resource, prop_viewer_resource)
        })

    # Handle access to the above where identifiers are present.
    # (This also happens when styles and scripts are being accessed through an
    # identified resource; for example: /event/some-event/styles/styles.css)

    view_choices.mapping[None] = ItemSelectorResource(editor_resource, view_choices, item_importer_resource,
        item_exporter_resource, prop_viewer_resource)

    item_choices = MapResource({
        # Item selectors...
        "event" : TypeSelectorResource(view_choices),
        "to-do" : TypeSelectorResource(view_choices),
        "card" : TypeSelectorResource(view_choices),
        "message" : TypeSelectorResource(view_choices),
        "calendar" : TypeSelectorResource(view_choices),
        # URI selectors producing views...
        "related-to" : FilterSelectorResource("related-to", view_choices, "to-do"),
        "person" : FilterSelectorResource("person", view_choices, "card"),
        # Exporters...
        "event.ics" : ExporterSelectorResource("event", collection_exporter_resource, prop_viewer_resource),
        "to-do.ics" : ExporterSelectorResource("to-do", collection_exporter_resource, prop_viewer_resource),
        "all.ics" : ExporterSelectorResource("all", collection_exporter_resource, prop_viewer_resource),
        # Views...
        "all" : view_choices,
        "" : TopSelectorResource("all/", webdav_root),
        None : view_choices
        }, pass_through=1)

    date_choices = MapResource({
        "date" : DateSelectorResource(item_choices, webdav_months),
        None : item_choices
        }, pass_through=1)

    return date_choices

# Resource preparation ahead of time - useful for making installations.

def prepare_resources():
    for cls in [ListViewerResource, CalendarViewerResource, PropertyViewerResource,
        ItemEditorResource, RootViewerResource, MonthViewerResource]:
        XSLForms.Resources.WebResources.prepare_resources(cls)

# vim: tabstop=4 expandtab shiftwidth=4
