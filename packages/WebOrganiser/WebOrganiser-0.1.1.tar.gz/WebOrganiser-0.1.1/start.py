#!/usr/bin/env python

"""
A simple start script which runs the BaseHTTPRequestHandler version but which
also sets up the environment first.
"""

import sys, os

# Try and find the applications.

program = os.path.abspath(sys.argv[0])
cwd = os.path.split(program)[0]

# Set up the environment and obtain the application resource.

applications = os.path.join(cwd, "applications")
if os.path.exists(applications):
    sys.path.insert(0, applications)

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
import WebCalendar
import WebCalendar.RDFAccess

# Get the store.

if len(sys.argv) > 2:
    store = WebCalendar.RDFAccess.open(sys.argv[1], sys.argv[2])
else:
    print "Need a store name and a store type (rdflib or sqltriples)."
    sys.exit(1)

# Get a simple Web site.

resource = WebCalendar.get_site(store)

print "Serving..."
try:
    deploy(resource, handle_errors=0)
finally:
    store.close()

# vim: tabstop=4 expandtab shiftwidth=4
