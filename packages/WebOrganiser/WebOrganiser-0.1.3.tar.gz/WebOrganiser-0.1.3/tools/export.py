#!/usr/bin/env python

import libxml2dom, WebCalendar.RDFAccess
import sys

if len(sys.argv) < 4:
    print "<store> <store-type> [<item-type> | <item-value> <output-filename>]"
    sys.exit(1)
else:
    store_name, store_type = sys.argv[1:3]

s = WebCalendar.RDFAccess.open(store_name, store_type)

if len(sys.argv) >= 5:
    item_value, output_filename = sys.argv[3:5]

    d = libxml2dom.createDocument(None, "export", None)
    l = s.get_selected_items([item_value])
    s.fill_element_serialised(d, d.xpath("*")[0], l, qualifier=(None, ""))
    f = open(output_filename, "wb")
    d.toFile(f, prettyprint=1)
    f.close()
else:
    item_type = sys.argv[3]

    for item in s.get_items_using_attributes({"item-type" : item_type}, []):
        print s.get_identifier_from_item(item)

# vim: tabstop=4 expandtab shiftwidth=4
