#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
import WebCalendar
import WebCalendar.RDFAccess
import sys

# Get the store.

if len(sys.argv) > 2:
    store = WebCalendar.RDFAccess.open(sys.argv[1], sys.argv[2])
else:
    print "Need a store name and a store type (rdflib or sqltriples)."
    sys.exit(1)

# Get a simple Web site.

resource = WebCalendar.get_site(store)

# Special magic incantation.

print "Serving..."
try:
    deploy(resource, handle_errors=0)
finally:
    store.close()

# vim: tabstop=4 expandtab shiftwidth=4
