#!/usr/bin/env python

from WebStack.Adapters.BaseHTTPRequestHandler import deploy
import WebCalendar
import WebCalendar.RDFAccess
import cmdsyntax

def main(argv):

    # Get the store.

    syntax = cmdsyntax.Syntax("""
        NAME TYPE [--module=MODULE_NAME] [--base=BASE_URI] [--host=HOST] [--port=PORT] [--debug]
        """)

    syntax_matches = syntax.get_args(argv[1:])

    try:
        args = syntax_matches[0]
        store = WebCalendar.RDFAccess.open(args["NAME"], args["TYPE"], base_uri=args.get("base"), database_module_name=args.get("module"),
            debug=args.has_key("debug"))
    except IndexError:
        print "Need a store name and a store type (rdflib or sqltriples)."
        print "For sqltriples, the database module name must also be given (PgSQL or pysqlite2)."
        print "An optional base URI can also be specified for permanent resource references."
        print "To change the server's address details, specify the optional host and port."
        print syntax.syntax
        return 1

    # Get a simple Web site.

    resource = WebCalendar.get_site(store)

    # Special magic incantation.

    print "Serving..."
    try:
        host = args.get("host", "")
        port = int(args.get("port", "8080"))
        deploy(resource, handle_errors=0, address=(host, port))
    finally:
        store.close()

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))

# vim: tabstop=4 expandtab shiftwidth=4
