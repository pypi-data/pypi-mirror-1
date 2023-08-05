#!/usr/bin/env python

"""
A Web calendar portal application.

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

__version__ = "0.2.5"

import os

# Site map imports.

from WebStack.Resources.ResourceMap import MapResource
from WebStack.Resources.Selectors import EncodingSelector
from WebStack.Resources.Static import DirectoryResource
from WebCalendarPortal.Viewer import *

# Important constants.

from WebCalendar.Common import encoding

# Site map initialisation.

def get_site(store):

    "Return a simple Web site resource for the given 'store'."

    # Get the main resources and the directory used by the application.

    index_resource = IndexViewerResource(store)

    # Set up file serving and some directory indexes.

    directory = os.path.join(os.path.split(__file__)[0], "Resources")
    styles_dir = DirectoryResource(os.path.join(directory, "styles"), {"css" : "text/css"})
    scripts_dir = DirectoryResource(os.path.join(directory, "scripts"), {"js" : "text/javascript"})
    images_dir = DirectoryResource(os.path.join(directory, "images"), {"png" : "image/png", "svg" : "image/svg+xml"})

    # Make a simple Web site.

    view_choices = MapResource({
        "styles" : styles_dir,
        "scripts" : scripts_dir,
        "images" : images_dir,
        "" : index_resource
        }) # not pass_through: identifiers are removed from the vpath

    return EncodingSelector(view_choices, encoding)

# Resource preparation ahead of time - useful for making installations.

def prepare_resources():
    for cls in [IndexViewerResource]:
        XSLForms.Resources.WebResources.prepare_resources(cls)

# vim: tabstop=4 expandtab shiftwidth=4
