#!/usr/bin/env python

from WebStack.Adapters.CGI import deploy
import WebCalendar
import WebOrganiser.RDFAccess
import RDFFormats.Store
import RDFCalendar.Store
import RDFMessage.Store

args = {
    "store" : "testdb",
    "module" : "PgSQL",
    "base" : "/"
    }

_store, _impl = RDFFormats.Store.open(args["store"], "sqltriples", database_module_name=args["module"],
    debug=args.has_key("debug"))
cstore = RDFCalendar.Store.Store(_store, _impl)
mstore = RDFMessage.Store.Store(_store, _impl)
store = WebOrganiser.RDFAccess.open(_store, [cstore, mstore], base_uri=args.get("base"))

# Get a simple Web site.

resource = WebCalendar.get_site(store)

# Special magic incantation.

try:
    deploy(resource, handle_errors=0)
finally:
    store.close()

# vim: tabstop=4 expandtab shiftwidth=4
