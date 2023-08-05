#!/usr/bin/env python

"""
A Web calendar application.

Copyright (C) 2005, 2006, 2007 Paul Boddie <paul@boddie.org.uk>

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

__version__ = "0.2.2"

import os

# Site map imports.

from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.Selectors import PathSelector
from WebStack.Resources.Static import DirectoryResource
from WebCalendar.Viewer import *
from WebCalendar.Selector import *
from WebCalendar.Editor import *
from WebCalendar.Exporter import *
from WebCalendar.Importer import *

# Important constants.

encoding = "utf-8"

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
    freebusy_exporter_resource = FreeBusyExporterResource(store)

    # Set up file serving and some directory indexes.

    directory = os.path.join(os.path.split(__file__)[0], "Resources")
    styles_dir = DirectoryResource(os.path.join(directory, "styles"), {"css" : "text/css"})
    scripts_dir = DirectoryResource(os.path.join(directory, "scripts"), {"js" : "text/javascript"})
    images_dir = DirectoryResource(os.path.join(directory, "images"), {"png" : "image/png", "svg" : "image/svg+xml"})
    webdav_root = RootViewerResource(store)
    webdav_months = MonthViewerResource()

    # Here's what the site looks like:

    """
    --> date_choices -------------> filter_choices -------------> item_choices -----------------> view_choices --> ItemSelectorResource
        |                        |  |                          |  | | |                        |  |
        | /date                  |  | /<filter>                |  | | | /<type>                |  | /
        |                        |  |                          |  | | |                        |  |
        -> DateSelectorResource --  -> FilterSelectorResource --  | | -> TypeSelectorResource --  -> ViewSelectorResource
                                                                  | |  
                                                                  | | /<filename>
                                                                  | |
                                                                  | -> ExporterSelectorResource
                                                                  | |
                                                                  | -> (FreeBusyExporterResource)
                                                                  |
                                                                  | /
                                                                  |
                                                                  -> TopSelectorResource

        Set year, month             Set filter-type,              Set item-type
                                    filter-item-value
    """

    # Make a simple Web site.

    view_choices = MapResource({
        "" : ViewSelectorResource(list_viewer_resource, calendar_viewer_resource, prop_viewer_resource)
        }, path_encoding=encoding) # not pass_through: identifiers are removed from the vpath

    # Handle access to the above where identifiers are present.
    # (This also happens when styles and scripts are being accessed through an
    # identified resource; for example: /event/some-event/styles/styles.css)

    view_choices.mapping[None] = ItemSelectorResource(editor_resource, view_choices, item_importer_resource,
        item_exporter_resource, prop_viewer_resource)

    item_choices = MapResource({
        # Exporters...
        "event.ics" : ExporterSelectorResource("event", collection_exporter_resource, prop_viewer_resource),
        "to-do.ics" : ExporterSelectorResource("to-do", collection_exporter_resource, prop_viewer_resource),
        "all.ics" : ExporterSelectorResource("all", collection_exporter_resource, prop_viewer_resource),
        "free-busy.ics" : ExporterSelectorResource("free-busy", freebusy_exporter_resource, prop_viewer_resource),
        # Views...
        "all" : view_choices,
        "" : TopSelectorResource("all/", webdav_root)
        }, pass_through=1, path_encoding=encoding)

    # Add type-based handlers, dependent on what the store offers.

    for item_type_name in store.get_supported_item_types():
        item_choices.mapping[item_type_name] = TypeSelectorResource(view_choices)

    filter_choices = MapResource({
        # URI selectors producing views...
        "related-to" : FilterSelectorResource("related-to", item_choices, prop_viewer_resource),
        "person" : FilterSelectorResource("person", item_choices, prop_viewer_resource, "card"),
        # Pass through...
        None : item_choices
        }, pass_through=1, path_encoding=encoding)

    date_choices = MapResource({
        "date" : DateSelectorResource(filter_choices, webdav_months),
        # Pass through...
        None : filter_choices
        }, pass_through=1, path_encoding=encoding)

    root_choices = MapResource({
        "styles" : styles_dir,
        "scripts" : scripts_dir,
        "images" : images_dir,
        None : date_choices
        }, pass_through=1, path_encoding=encoding)

    return PathSelector(root_choices)

# Resource preparation ahead of time - useful for making installations.

def prepare_resources():
    for cls in [ListViewerResource, CalendarViewerResource, PropertyViewerResource,
        ItemEditorResource, RootViewerResource, MonthViewerResource]:
        XSLForms.Resources.WebResources.prepare_resources(cls)

# vim: tabstop=4 expandtab shiftwidth=4
