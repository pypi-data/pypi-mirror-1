#! /usr/bin/env python

from distutils.core import setup
import os

import WebOrganiser

setup(
    name         = "WebOrganiser",
    description  = "A distribution of Web applications providing access to calendar, contact and message stores",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/WebOrganiser.html",
    version      = WebOrganiser.__version__,
    package_dir  = {"WebCalendar" : os.path.join("applications", "WebCalendar"),
                    "WebCalendarPortal" : os.path.join("applications", "WebCalendarPortal")},
    packages     = ["WebCalendar", "WebCalendarPortal", "WebOrganiser"],
    package_data = {"WebCalendar" : [
                        "Resources/*.xsl", "Resources/*.xhtml", "Resources/*.xml",
                        "Resources/scripts/*.js", "Resources/styles/*.css",
                        "Resources/images/*.png", "Resources/images/*.svg",
                        "Resources/images/*.txt"],
                    "WebCalendarPortal" : [
                        "Resources/*.xsl", "Resources/*.xhtml", "Resources/*.xml",
                        "Resources/styles/*.css"]},
    scripts      = ["servers/BaseHTTPRequestHandler/WebCalendarApp.py",
                    "servers/BaseHTTPRequestHandler/WebCalendarPortalApp.py"]
    )
