#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
import WebCalendarPortal
import WebOrganiser.RDFAccess
import RDFFormats.Store
import RDFCalendar.Store
import RDFMessage.Store
import cmdsyntax

def main(argv):

    # Get the store.

    syntax = cmdsyntax.Syntax("""
        --store=NAME --module=MODULE_NAME [--base=BASE_URI] [--host=HOST] [--port=PORT] [--debug]
        """)

    syntax_matches = syntax.get_args(argv[1:])

    try:
        args = syntax_matches[0]
        _store, _impl = RDFFormats.Store.open(args["store"], "sqltriples", database_module_name=args["module"],
            debug=args.has_key("debug"))
        cstore = RDFCalendar.Store.Store(_store, _impl)
        mstore = RDFMessage.Store.Store(_store, _impl)
        store = WebOrganiser.RDFAccess.open(_store, [cstore, mstore], base_uri=args.get("base"))
    except IndexError:
        print "Need a store name and the database module name (PgSQL or pysqlite2)."
        print "An optional base URI can also be specified for permanent resource references."
        print "To change the server's address details, specify the optional host and port."
        print syntax.syntax
        return 1

    # Get a simple Web site.

    resource = WebCalendarPortal.get_site(store)

    # Special magic incantation.

    print "Serving..."
    try:
        host = args.get("host", "")
        port = int(args.get("port", "8081"))
        deploy(resource, handle_errors=0, address=(host, port))
    finally:
        store.close()

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))

# vim: tabstop=4 expandtab shiftwidth=4
