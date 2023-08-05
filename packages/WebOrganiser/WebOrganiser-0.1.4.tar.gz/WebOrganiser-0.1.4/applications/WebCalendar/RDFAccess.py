#!/usr/bin/env python

"""
Access to RDF stores.

Copyright (C) 2005, 2006 Paul Boddie <paul@boddie.org.uk>

This software is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with this library; see the file LICENCE.txt
If not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

from RDFCalendar.Format import property_names, permitted_attributes, get_attribute_label
from RDFCalendar.Writers import write_to_document
import RDFCalendar.Store
import RDFCalendar.Parsers

class Store:

    "A convenience wrapper around RDF stores."

    def __init__(self, store, base_uri="/"):

        """
        Initialise with a store found with the given underlying 'store' and an
        optional 'base_uri' which can be used to qualify URI references.
        """

        self.cstore = store
        self.base_uri = self.cstore.Namespace(base_uri)

        # Copy in useful attributes.

        self.Literal = self.cstore.Literal
        self.Namespace = self.cstore.Namespace
        self.URIRef = self.cstore.URIRef
        self.BNode = self.cstore.BNode
        self.TYPE = self.cstore.TYPE
        self.rdfcalendar = self.cstore.rdfcalendar
        self.rdfsms = self.Namespace("http://www.boddie.org.uk/ns/rdfsms/")

        # Other useful values.

        self.rdfcalendar_uid = unicode(self.rdfcalendar) + "uid#"

    def get_context(self, context):

        """
        Return a copy of this store which uses the given 'context' to constrain
        operations on the stored triples.
        """

        return self.__class__(self.cstore.get_context(context))

    def contexts(self):

        "Return a list of contexts found in this store."

        return self.cstore.contexts()

    def close(self):

        "Close the underlying store."

        self.cstore.close()

    def commit(self):

        "Commit changes to the underlying store if appropriate."

        self.cstore.commit()

    def rollback(self):

        "Roll back changes to the underlying store if appropriate."

        self.cstore.rollback()

    def remove_context(self, context):

        """
        Removes the specified 'context' from the database.
        """

        self.cstore.remove_context(context)

    # Low-level query methods.

    def get_comparison(self, comparison, values):

        """
        Return a comparison expression for the given 'comparison' and 'value',
        suitable for triple stores which support querying.
        """

        # NOTE: Permits precise matching of URIRefs.

        if len(values) == 1 and comparison is None:
            return values[0]

        # NOTE: Permits literal matching.

        expressions = []
        object_type = "U"
        for value in values:
            if not isinstance(value, self.URIRef):
                object_type = "L"
            if comparison == "startswith":
                expressions.append("substr(_, 1, %s) = ?" % len(value))
            else:
                expressions.append("_ = ?")
        return self.cstore.store.Expression("(" + " or ".join(expressions) + ")", values, object_type)

    def get_items_with_property(self, property_type, property_value, comparison=None):

        """
        Return all items with the given 'property_type' and 'property_value'.

        If the optional 'comparison' is specified using a string method name,
        each item's value for the stated 'property_type' will be asked to
        provide a method of that name, and if the given 'property_value' passed
        as a parameter to that method causes a true value to be returned, the
        item will be added to the result list.
        """

        for _item, _property_type, _property_value in self.get_triples_with_property(property_type, property_value, None, comparison=comparison):
            yield _item

    def get_triples_with_property(self, property_type, property_value, item, comparison=None):
        if comparison is None:
            for _item, _property_type, _property_value in self.cstore.store.triples((item, property_type, property_value)):
                yield _item, _property_type, _property_value
        else:
            for _item, _property_type, _property_value in self.cstore.store.triples((item, property_type, None)):
                if property_value is None or \
                    comparison is None and _property_value == property_value or \
                    comparison is not None and hasattr(_property_value, comparison) and getattr(_property_value, comparison)(property_value):
                    yield _item, _property_type, _property_value

    def get_owner_items_with_properties(self, property_types, property_values, comparison=None):

        """
        Return all items containing nodes having the given 'property_types' and
        final 'property_values'.

        If the optional 'comparison' is specified using a string method name,
        each item's value for the stated 'property_type' will be asked to
        provide a method of that name, and if the given 'property_value' passed
        as a parameter to that method causes a true value to be returned, the
        item will be used to find suitable owner items.
        """

        reversed_types = property_types[:]
        reversed_types.reverse()

        for property_value in property_values:
            for item, _property_type, _property_value in self.get_triples_with_property(reversed_types[0], property_value, None, comparison=comparison):
                current_item = item
                for property_type in reversed_types[1:]:
                    owner_item = None
                    for owner_item in self.get_items_with_property(property_type, current_item):
                        break
                    current_item = owner_item
                    if current_item is None:
                        break
                if current_item is not None:
                    yield current_item

    def get_owner_items_using_query(self, property_types, property_values, comparison):
        reversed_types = property_types[:]
        reversed_types.reverse()

        # NOTE: Permits negation.

        if len(property_values) == 0:
            query = self.get_comparison(None, [self.cstore.store.Defined()])
        else:
            query = self.get_comparison(comparison, property_values)

        # Build the subselect hierarchy.

        for property_type in reversed_types:
            query = self.cstore.store.subjects(property_type, query)

        # NOTE: The actual negation.

        if len(property_values) == 0:
            query = self.cstore.store.subjects(pattern=[self.cstore.store.negation(query)])

        return query

    def get_item_type(self, item):

        "Return the type of the given 'item'."

        return self.cstore.get_node_type(item)

    def get_item_properties(self, item):

        """
        Return the properties of the given 'item' as 2-tuples - the type and
        value of each property.
        """

        for _item, property_type, property_value in self.cstore.store.triples((item, None, None)):
            yield property_type, property_value

    # Reporting methods.
    # These methods are used to supply templates with item information.

    def fill_element_serialised(self, doc, element, items, qualifier=None):

        """
        Within the given document 'doc', inside the given 'element', insert the
        XML serialisation of each item in the supplied 'items'.

        The fill_element_serialised method provides an accurate rendition of
        each item in RDFCalendar's XML format.
        """

        write_to_document(doc, element, self.cstore, nodes=items, qualifier=qualifier, value_as_attribute=1)

    def fill_element(self, doc, element, items, element_name="item", top_level=1):

        """
        Within the given document 'doc', inside the given 'element', insert the
        top-level details of the given 'items'. Each item will be represented by
        an element of the optional 'element_name' (or the default name, "item").

        The fill_element method provides item summaries, more appropriate for
        list views. Typically, each item will look something like this:

        <item item-value="..." item-type="..." prop1="..." prop2="..." />
        """

        for item in items:
            item_element = element.appendChild(doc.createElement(element_name))

            # Introduce the identifier form of items.
            item_value = self.get_identifier_from_item(item)
            item_element.setAttribute("item-value", item_value)

            properties = {}
            for property_type, property_value in self.get_item_properties(item):
                label = self.get_label(property_type)

                # Write property values to attributes.

                if isinstance(property_value, self.Literal):
                    item_element.setAttribute(label, unicode(property_value))

                # Write item types out nicely.

                elif label == "item-type":
                    item_element.setAttribute(label, self.get_label(property_value))

                # Write entire items out at the top level.

                elif top_level:
                    self.fill_element(doc, item_element, [property_value], label, 0)

                # For URIRef-based properties, write identifiers out.

                else:
                    item_element.setAttribute(label, self.get_identifier_from_item(property_value))

    # Update methods.

    def add_item(self, item, doc):

        """
        Add an 'item' to the store using the definition document 'doc'.
        If 'item' is None, a new item will be added to the store.
        """

        doc_root = doc.xpath("item/*")[0]
        uriref = self.get_uriref(item)
        RDFCalendar.Parsers.parse_document_fragment(doc, doc_root, self.cstore, uriref=uriref)
        self.commit()

    def remove_item(self, item, deep=0):

        "Remove the given 'item' from the store."

        self.cstore.remove_node(item, deep)
        self.commit()

    def has_item(self, item):

        "Return whether the store contains the given 'item'."

        return self.cstore.has_triple((item, None, None))

    # Conversions from items to identifiers and back again.

    def get_item_from_identifier(self, identifier):

        """
        Return an item built from the given 'identifier'. Here, we distinguish
        between BNode, URIRef including a uid, URIRef within the store, and
        other URIRef items as follows:

        BNode                               starts with _
        URIRef/uid                          starts with --
        URIRef within base URI for store    unprefixed (add the base URI)
        URIRef                              starts with -
        """

        if identifier.startswith("_"):
            return self.BNode(identifier)
        elif identifier.startswith("--"):
            return self.URIRef(self.rdfcalendar_uid + identifier[2:])
        elif identifier.startswith("-"):
            return self.URIRef(identifier[1:])
        else:
            return self.base_uri[identifier]

    def get_item_from_reference(self, reference):

        """
        Similar to get_item_from_identifer, but with a narrower range of types,
        return an item for the given 'reference' according to the following
        mapping:

        BNode                               starts with _
        URIRef                              all other symbols

        NOTE: This is dependent on referenced items being defined by/under BNode
        NOTE: objects, but this is probably going to be phased out.
        """

        if reference.startswith("_"):
            return self.BNode(reference)
        else:
            return self.URIRef(reference)

    def get_identifier_from_item(self, item):

        """
        Return an identifier built from the given 'item'. Here, we distinguish
        between BNode, URIRef including a uid, URIRef within the store, and
        other URIRef items as follows:

        BNode                               starts with _
        URIRef/uid                          starts with --
        URIRef within base URI for store    unprefixed (remove the base URI)
        URIRef                              starts with -
        """

        item_str = unicode(item)

        if isinstance(item, self.URIRef):
            # URIRef/uid:
            if item_str.startswith(self.rdfcalendar_uid):
                # NOTE: Taken from RDFCalendar.
                return "--" + item_str[len(self.rdfcalendar_uid):]
            # URIRef within base URI for store:
            elif item_str.startswith(unicode(self.base_uri)):
                return item_str[len(unicode(self.base_uri)):]
            # Other URIRef:
            else:
                return "-" + item_str
        else:
            # BNodes should begin with _.
            return unicode(item)

    # Convenience methods.

    def get_label(self, identifier):

        "Return a label for a (typically) type-based 'identifier'."

        if identifier == self.TYPE:
            return "item-type"
        else:
            label = self.cstore.get_label(identifier)
            if label is None:
                label = identifier.split("/")[-1]
            return label

    def get_uid(self, identifier):

        """
        Return a unique identifier label for the given 'identifier' or None
        if the 'identifier' cannot be interpreted in such a way.
        """

        return self.cstore.get_uid(identifier)

    def get_uriref(self, item):

        """
        Return the given 'item' as a URIRef or None if the 'item' is not of a
        compatible/equivalent nature.
        """

        if isinstance(item, self.URIRef):
            return item
        else:
            return None

    # Filtering conversion methods.

    def get_item_type_from_identifier(self, identifier):

        # NOTE: Make this more general.

        if identifier in property_names.keys():
            return self.rdfcalendar[identifier]
        elif identifier == "message":
            return self.rdfsms[identifier]
        else:
            return None

    def get_identifier_from_item_type(self, item_type):

        # NOTE: Make this more general.

        item_type_str = unicode(item_type)
        if item_type_str.startswith(self.rdfcalendar):
            return item_type_str[len(self.rdfcalendar):]
        elif item_type_str.startswith(self.rdfsms):
            return item_type_str[len(self.rdfsms):]
        else:
            return None

    def get_property_type_from_identifier(self, identifier):
        if identifier == "item-type":
            return self.TYPE
        elif identifier is None:
            return None
        else:
            return self.rdfcalendar[identifier]

    def get_value_from_identifier(self, property_type, value):
        if value is None:
            return None
        elif property_type == self.TYPE:
            return self.get_item_type_from_identifier(value)
        elif property_type in (self.rdfcalendar["related-to"], self.rdfcalendar["uri"]):
            return self.get_item_from_identifier(value)
        else:
            return self.Literal(value)

    # Querying methods.

    def get_selected_items(self, values):

        """
        Return a list of items found using the given 'values': a list of unique
        identifiers each corresponding to an item.
        """

        items = []
        for value in values:
            items.append(self.get_item_from_identifier(value))
        return unique(items)

    def get_filtered_items(self, filters):

        """
        Return a list of items filtered using information from 'filters', which
        consists of a list of 2-tuples, each containing a list of simple type
        labels (eg. ["uid"], ["dtstart", "datetime"]) and either a list of
        simple values (eg. ["20050827", "20050828"]) or a 2-tuple describing the
        comparison and a single value (eg. ("startswith", "200508")).
        """

        new_filters = []
        for names, values in filters:

            # Get the actual property types.

            property_types = []
            for name in names:
                property_types.append(self.get_property_type_from_identifier(name))

            # Get suitably prepared values.

            property_values = []
            if isinstance(values, tuple):
                comparison, value = values
                property_value = self.get_value_from_identifier(property_types[-1], value)
                property_values.append(property_value)
            else:
                comparison = None
                for value in values:
                    property_value = self.get_value_from_identifier(property_types[-1], value)
                    property_values.append(property_value)
            new_filters.append((property_types, property_values, comparison))

        if getattr(self.cstore.store, "supports_querying", 0):
            return self.get_filtered_items_using_query(new_filters)
        else:
            return self.get_filtered_items_manually(new_filters)

    def get_filtered_items_manually(self, filters):
        results = []
        for property_types, property_values, comparison in filters:
            results += self.get_owner_items_with_properties(property_types, property_values, comparison=comparison)
        return unique(results)

    def get_filtered_items_using_query(self, filters):
        queries = []
        for property_types, property_values, comparison in filters:
            queries.append(self.get_owner_items_using_query(property_types, property_values, comparison=comparison))
        return self.cstore.store.union(queries)

    def combine_items(self, results):
        if getattr(self.cstore.store, "supports_querying", 0):
            return self.combine_items_using_query(results)
        else:
            return self.combine_items_manually(results)

    def combine_items_manually(self, results):
        found_items = results[0]
        for result in results[1:]:
            found_items = self._combine_items_manually(found_items, result)
        return found_items

    def _combine_items_manually(self, existing_items, items):
        results = []
        for item in existing_items:
            if item in items:
                results.append(item)
        return results

    def combine_items_using_query(self, results):
        return self.cstore.store.intersection(results)

    def get_items_using_attributes(self, attributes, default_item_types):

        """
        To query the store, prepare filters, taking information from the given
        'attributes' and adding the 'default_item_types' where appropriate, and
        return a list of items.
        """

        # NOTE: Despite potentially flexible support for querying in sqltriples,
        # NOTE: sqlite doesn't seem to support more than simple left-to-right
        # NOTE: evaluation of union/intersect with select statements. Thus, we
        # NOTE: must be careful with the criteria below.

        results = []

        # Use filtering categories.

        if attributes.has_key("filter-item-value"):
            filters = []
            filter_item_value = attributes["filter-item-value"]

            # Use related-to criteria.

            if attributes.get("filter-type") == "related-to":
                filters.append((["related-to"], [filter_item_value]))

            # Or use person-related criteria.

            elif attributes.get("filter-type") == "person":
                filters.append((["organizer", "uri"], [filter_item_value]))
                filters.append((["attendee", "uri"], [filter_item_value]))

            # Or specify non-related-to items.
            # NOTE: Hack used to optimise sqltriples-based querying.

            elif getattr(self.cstore.store, "supports_querying", 0):
                filters.append((["related-to"], []))

            results.append(self.get_filtered_items(filters))

        # NOTE: Hack used to optimise sqltriples-based querying.

        elif getattr(self.cstore.store, "supports_querying", 0):
            filters = []
            filters.append((["related-to"], []))
            results.append(self.get_filtered_items(filters))

        # Date-based filtering.

        if attributes.get("year") is not None:
            if attributes.get("month") is not None:
                if attributes.get("day") is not None:
                    pattern = ("startswith", "%04d%02d%02d" % (attributes["year"], attributes["month"], attributes["day"]))
                else:
                    pattern = ("startswith", "%04d%02d" % (attributes["year"], attributes["month"]))
            else:
                pattern = ("startswith", "%04d" % attributes["year"])

            filters = []
            #filters.append((["dtstart", "datetime"], pattern))
            #filters.append((["dtend", "datetime"], pattern))
            filters.append(([None, "datetime"], pattern))
            results.append(self.get_filtered_items(filters))

        # Or use type-based criteria.

        if attributes.has_key("item-type"):
            item_types = [attributes["item-type"]]
        else:
            item_types = default_item_types

        filters = []
        filters.append((["item-type"], item_types))

        results.append(self.get_filtered_items(filters))

        # Combine the results.

        return self.combine_items(results)

def open(store_name, store_type, base_uri=None, context=None, **kw):
    store = RDFCalendar.Store.open(store_name, store_type, context, **kw)
    if base_uri is not None:
        return Store(store, base_uri)
    else:
        return Store(store)

def unique(l):
    d = {}
    for i in l:
        d[i] = None
    return d.keys()

# vim: tabstop=4 expandtab shiftwidth=4
