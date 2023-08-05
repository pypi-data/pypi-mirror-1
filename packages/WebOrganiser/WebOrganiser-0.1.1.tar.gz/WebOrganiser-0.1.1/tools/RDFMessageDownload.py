#!/usr/bin/env python

"""
Download messages from storage on the telephone, storing them in an RDF data store.
"""

from T616 import T616, CommandException
import WebCalendar.RDFAccess
import locale

c20_start = 90
cmd_charset = locale.getdefaultlocale()[1]
sms_charset = "UTF-8" # Not sensible to change this, since the telephone only
                      # supports a few charsets.

def convert_datetime(date, time):
    t = date.split("/")
    year, month, day = map(int, t)

    # Fix Y2K shortsightedness.

    if year < c20_start:
        year = 2000 + year
    else:
        year = 1900 + year

    # NOTE: Ignoring time zone.

    d = time.split("+")
    d = d[0].split("-")
    d = d[0].split(":")
    hour, minute, second = map(int, d)

    return "%04d%02d%02dT%02d%02d%02dZ" % (year, month, day, hour, minute, second)

if __name__ == "__main__":
    import sys
    import cmdsyntax
    import time

    # Find the documents.

    syntax = cmdsyntax.Syntax("""
        --store=STORE_NAME
        --store-type=STORE_TYPE
        --ns=NAMESPACE
        --identity=IDENTITY
        [--memory=MEMORY]
        [--bdaddr=ADDRESS]
        [--channel=CHANNEL]
        [--port=PORT]
        [--baudrate=BAUD_RATE]
        [--remove]
        """)

    syntax_matches = syntax.get_args(sys.argv[1:])

    try:
        args = syntax_matches[0]
    except IndexError:
        print "Here is the syntax:"
        print syntax.syntax
        print
        print "Need the following:"
        print
        print "STORE_NAME - an RDF data store filename or database name"
        print "STORE_TYPE - rdflib or sqltriples"
        print "NAMESPACE  - the unique namespace identifier for the messages"
        print "IDENTITY   - the identity of the owner of the telephone"
        print "             eg. Paul"
        print "MEMORY     - typically SM or ME - the telephone memory to be accessed"
        print "ADDRESS    - the address of the telephone"
        print "             eg. 01:23:45:67:89:AB"
        print "CHANNEL    - the communications channel to be used"
        print "             eg. 1"
        print "PORT       - the device or port to be used to connect to the telephone"
        print "             eg. /dev/rfcomm0"
        print "BAUD_RATE  - the connection speed to be used"
        print "             eg. 57600"
        sys.exit(1)

    # Open the store.

    store = WebCalendar.RDFAccess.open(args["store"], args["store-type"], context=args["ns"])
    cstore = store.cstore
    istore = cstore.store

    # Test for removal of existing messages from the data store.

    if args.has_key("remove"):
        if args["store-type"] == "rdflib":
            istore.remove_context(store.URIRef(args["ns"]))
        else:
            print "Removal not supported for this store type."
        sys.exit(1)

    # Otherwise, look for communications arguments.

    if args.has_key("port"):
        if args.has_key("baudrate"):
            p = T616(port=args["port"], baudrate=int(args["baudrate"]), debug=0)
        else:
            p = T616(port=args["port"], debug=0)
    else:
        if args.has_key("channel"):
            p = T616(bdaddr=args["bdaddr"], channel=int(args["channel"]), debug=0)
        else:
            p = T616(bdaddr=args["bdaddr"], debug=0)

    # Get the memory argument.

    if args.has_key("memory"):
        memory = args["memory"]
    else:
        memory = "SM"

    # Get the identity.

    identity = args["identity"]

    # Get the namespace.

    ns = store.Namespace(args["ns"])

    # Attempt to retrieve the messages.

    try:
        p.selectMessageStorage(memory)

        # Select the message format.

        p.setCharacterSet(sms_charset)
        p.setMessageFormat(p.TEXT)

        # Read the messages.

        try:
            messages = p.readMessages()
            print "Read %d messages from %s" % (len(messages), memory)
    
            for header, message in messages:
                index, status = header[0:2]
                message_id = "%s-%s" % (memory, index)

                # Where more information exists, add nodes to represent it.

                if len(header) >= 6:
                    number, name, date, time = header[2:6]
                    created = store.BNode()
                    istore.add((ns[message_id], store.rdfsms["created"], created))
                    istore.add((created, store.rdfcalendar["datetime"], store.Literal(convert_datetime(date, time))))
                    sender = store.BNode()
                    istore.add((ns[message_id], store.rdfsms["sender"], sender))
                    istore.add((sender, store.rdfcalendar["name"], store.Literal(unicode(name, sms_charset))))
                    istore.add((sender, store.rdfsms["number"], store.Literal(unicode(number, sms_charset))))

                # Otherwise, fill in the gaps.

                else:
                    sender = store.BNode()
                    istore.add((ns[message_id], store.rdfsms["sender"], sender))
                    istore.add((sender, store.rdfcalendar["name"], store.Literal(unicode(identity, cmd_charset))))

                # Add basic message information.

                istore.add((ns[message_id], store.rdfsms["status"], store.Literal(status)))
                istore.add((ns[message_id], store.rdfsms["index"], store.Literal(index)))
                istore.add((ns[message_id], store.rdfsms["memory"], store.Literal(memory)))
                istore.add((ns[message_id], store.TYPE, store.rdfsms["message"]))
                body = store.BNode()
                istore.add((ns[message_id], store.rdfsms["body"], body))
                istore.add((body, store.rdfcalendar["details"], store.Literal(unicode(message, sms_charset))))

            store.commit()
            print "Wrote to store %s" % args["store"]

        except CommandException, exc:
            store.rollback()
            print "Reading failed with exception:", str(exc)

    finally:
        p.close()
        store.close()

# vim: tabstop=4 expandtab shiftwidth=4
