#!/usr/bin/env python

import libxml2dom, WebCalendar.RDFAccess

if __name__ == "__main__":
    import sys
    import cmdsyntax

    # Find the documents.

    syntax = cmdsyntax.Syntax("""
        --store=STORE_NAME
        --store-type=STORE_TYPE
        [--module=MODULE]
        [--base=BASE_URI]
        [--context=CONTEXT]
        (--item-type=ITEM_TYPE | (--item-value=ITEM_VALUE --output-xml=OUTPUT_FILENAME))
        """)

    syntax_matches = syntax.get_args(sys.argv[1:])

    try:
        args = syntax_matches[0]
    except IndexError:
        print "Here is the syntax:"
        print syntax.syntax
        sys.exit(1)

    s = WebCalendar.RDFAccess.open(args["store"], args["store-type"], base_uri=args.get("base"), database_module_name=args.get("module"))

    if args.has_key("item-value"):
        d = libxml2dom.createDocument(None, "export", None)
        l = s.get_selected_items([args["item-value"]])
        s.fill_element_serialised(d, d.xpath("*")[0], l, qualifier=(None, ""))
        f = open(args["output-xml"], "wb")
        d.toFile(f, prettyprint=1)
        f.close()
    else:
        for item in s.get_items_using_attributes({"item-type" : args["item-type"]}, []):
            print s.get_identifier_from_item(item)

# vim: tabstop=4 expandtab shiftwidth=4
