#! /usr/bin/env python

from distutils.core import setup
import sys, os

# Try and find the applications.

program = os.path.abspath(sys.argv[0])
cwd = os.path.split(program)[0]

# Set up the environment and obtain the application resource.

applications = os.path.join(cwd, "applications")
sys.path.append(applications)

import WebCalendar

setup(
    name         = "WebOrganiser",
    description  = "A distribution of Web applications providing access to calendar, contact and message stores",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/WebOrganiser.html",
    version      = WebCalendar.__version__,
    package_dir  = {"" : "applications"},
    packages     = ["WebCalendar"],
    package_data = {"WebCalendar" : ["Resources/*.xsl", "Resources/*.xhtml", "Resources/*.xml",
                                     "Resources/scripts/*.js", "Resources/styles/*.css",
                                     "Resources/images/*.png", "Resources/images/*.svg",
                                     "Resources/images/*.txt"]},
    scripts      = ["servers/BaseHTTPRequestHandler/WebCalendarApp.py"]
    )
