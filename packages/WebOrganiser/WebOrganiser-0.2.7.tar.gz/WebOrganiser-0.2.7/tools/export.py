#!/usr/bin/env python

import libxml2dom
import WebOrganiser.RDFAccess
import RDFCalendar.Store
import RDFMessage.Store
import RDFFormats.Store

if __name__ == "__main__":
    import sys
    import cmdsyntax

    # Find the documents.

    syntax = cmdsyntax.Syntax("""
        --store=STORE_NAME
        [--store-type=STORE_TYPE]
        [--module=MODULE]
        [--base=BASE_URI]
        [--context=CONTEXT]
        (--item-type=ITEM_TYPE | (--item-value=ITEM_VALUE --simple --output-xml=OUTPUT_FILENAME))
        [--debug]
        """)

    syntax_matches = syntax.get_args(sys.argv[1:])

    try:
        args = syntax_matches[0]
    except IndexError:
        print "Here is the syntax:"
        print syntax.syntax
        sys.exit(1)

    _store, _impl = RDFFormats.Store.open(args["store"], args.get("store-type", "sqltriples"), database_module_name=args.get("module"),
        debug=args.has_key("debug"))
    cstore = RDFCalendar.Store.Store(_store, _impl)
    mstore = RDFMessage.Store.Store(_store, _impl)
    store = WebOrganiser.RDFAccess.open(_store, [cstore, mstore], base_uri=args.get("base"))

    if args.has_key("item-value"):
        d = libxml2dom.createDocument(None, "export", None)
        l = store.get_selected_items([args["item-value"]])
        if args.has_key("simple"):
            store.fill_element(d, d.xpath("*")[0], l)
        else:
            store.fill_element_serialised(d, d.xpath("*")[0], l, qualifier=(None, ""))
        f = open(args["output-xml"], "wb")
        d.toFile(f, prettyprint=1)
        f.close()
    else:
        items = store.get_items_using_attributes({"item-type" : args["item-type"]})
        for item in items:
            print store.get_identifier_from_item(item)

# vim: tabstop=4 expandtab shiftwidth=4
