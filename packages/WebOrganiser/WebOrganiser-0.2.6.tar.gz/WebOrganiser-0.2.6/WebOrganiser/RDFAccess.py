#!/usr/bin/env python

"""
Access to RDF stores.

Copyright (C) 2005, 2006, 2007 Paul Boddie <paul@boddie.org.uk>

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

class DuplicateResourceError(Exception):
    pass

class NotSupportedError(Exception):
    pass

class Store:

    "A convenience wrapper around RDF stores."

    DuplicateResourceError = DuplicateResourceError

    def __init__(self, store, handlers, base_uri="/"):

        """
        Initialise with the given underlying 'store', a 'handlers' collection,
        and an optional 'base_uri' which can be used to qualify URI references.
        """

        self.store = store
        self.handlers = handlers
        self.base_uri = self.store.Namespace(base_uri)

        # Copy in useful attributes.

        self.Literal = self.store.Literal
        self.Namespace = self.store.Namespace
        self.URIRef = self.store.URIRef
        self.BNode = self.store.BNode
        self.TYPE = self.store.TYPE

        # Initialise some useful data.

        self.default_item_types = []
        for handler in self.handlers:
            for item_type in handler.get_supported_item_types():
                self.default_item_types.append(item_type)

    # Handler selection methods.

    def get_handler(self, item):

        "Return the handler suitable for processing the given 'item'."

        # First get the item type.

        item_type = self.get_item_type(item)
        if item_type is not None:
            item_type_name = self.get_identifier_from_item_type(item_type)
            return self.get_handler_for_item_type_name(item_type_name)
        else:
            return None

    def get_handler_for_item_type_name(self, item_type_name):

        """
        Return the handler capable of processing items having the given
        'item_type_name'.
        """

        for handler in self.handlers:
            if handler.supports_item_type(item_type_name):
                return handler
        return None

    def get_supported_item_types(self):

        "Return a list of all item types supported by the handlers."

        return self.default_item_types

    def get_urirefs_for_item_type(self, item_type_name):

        """
        Query the handlers and return a list of URIRefs which can represent the
        given 'item_type_name'.
        """

        urirefs = []
        for handler in self.handlers:
            urirefs += handler.get_urirefs_for_item_type(item_type_name)
        return urirefs

    def get_urirefs_for_property_type(self, property_type_name):

        """
        Query the handlers and return URIRefs which can represent the given
        'property_type_name'.
        """

        urirefs = []
        for handler in self.handlers:
            urirefs += handler.get_urirefs_for_property_type(property_type_name)
        return urirefs

    def get_property_types_for_uriref(self, uriref):

        """
        Query the handlers and return the abstract property types which the
        given 'uriref' can represent.
        """

        property_types = []
        for handler in self.handlers:
            property_types += handler.get_property_types_for_uriref(uriref)
        return property_types

    def get_urirefs_for_attribute(self, attribute):

        """
        Query the handlers and return lists of URIRefs which can represent the
        given 'attribute'.
        """

        urirefs = []
        for handler in self.handlers:
            urirefs += handler.get_urirefs_for_attribute(attribute)
        return urirefs

    def get_predicates_for_attribute(self, attribute):

        """
        Query the handlers and return a tuple of predicates which can represent
        the given 'attribute'.
        """

        urirefs = self.get_urirefs_for_attribute(attribute)
        if not urirefs:
            return ()

        # Convert the URIRefs into a list of predicate lists.

        predicates = [[p] for p in urirefs[0]]

        # For each URIRef list, traverse from right to left, combining the
        # contents with the predicates, adding extra elements on the left if
        # necessary.

        for l in urirefs[1:]:
            np = len(predicates)
            for i in range(0, len(l)):
                uriref = l[-1-i]
                predicate = predicates[-1-i]
                if i >= np:
                    predicates.insert(0, uriref)
                else:
                    if uriref not in predicate:
                        predicate.append(uriref)

        return tuple(predicates)

    # Standard store methods.

    def get_context(self, context):

        """
        Return a copy of this store which uses the given 'context' to constrain
        operations on the stored triples.
        """

        return self.__class__(self.store.get_context(context))

    def contexts(self):

        "Return a list of contexts found in this store."

        return self.store.contexts()

    def close(self):

        "Close the underlying store."

        self.store.close()

    def commit(self):

        "Commit changes to the underlying store if appropriate."

        self.store.commit()

    def rollback(self):

        "Roll back changes to the underlying store if appropriate."

        self.store.rollback()

    def remove_context(self, context):

        """
        Removes the specified 'context' from the database.
        """

        self.store.remove_context(context)

    # Low-level query methods.

    def get_comparison(self, comparison, values):

        """
        Return a comparison expression for the given 'comparison' and 'values',
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
            elif comparison == "contains":
                expressions.append("_ like ?")
            else:
                expressions.append("_ = ?")
        return self.store.Expression("(" + " or ".join(expressions) + ")", values, object_type)

    def get_item_type(self, item):

        "Return the type of the given 'item'."

        # NOTE: Taken from RDFCalendar.Store.Store.

        for s, p, node_type in self.store.triples((item, self.TYPE, None)):
            return node_type
        return None

    # Reporting methods.
    # These methods are used to supply templates with item information.

    def fill_element_serialised(self, doc, element, items, qualifier=None):

        """
        Within the given document 'doc', inside the given 'element', insert the
        XML serialisation of each item in the supplied 'items'.

        The fill_element_serialised method provides an accurate rendition of
        each item in RDFCalendar's XML format.
        """

        for item in items:
            handler = self.get_handler(item)
            if handler is not None:
                handler.write_to_document(doc, element, nodes=[item], qualifier=qualifier, value_as_attribute=1)

    def fill_element(self, doc, element, items, element_name="item"):

        """
        Within the given document 'doc', inside the given 'element', insert the
        top-level details of the given 'items'. Each item will be represented by
        an element of the optional 'element_name' (or the default name, "item").

        The fill_element method provides item summaries, more appropriate for
        list views. Typically, each item will look something like this:

        <item item-value="..." item-type="...">
          <prop1 attrA="..."/>
          <prop2 attrB="..."/>
        </item>
        """

        properties = self.store.tuples((items, None, None, None), partial=1, order_by="subject", ordering="asc")
        current_item = None
        current_property_type = None

        for property in properties:
            if len(property) == 4:
                item, property_type1, property_type2, property_value = property
            else:
                item, property_type1, property_value = property
                property_type2 = None

            # Add an element for each item.

            if item != current_item:
                item_element = element.appendChild(doc.createElement(element_name))

                # Introduce the identifier form of items.

                item_value = self.get_identifier_from_item(item)
                item_element.setAttribute("item-value", item_value)

                # Remember the current item and control the production of
                # elements.

                current_item = item
                property_labels1 = {}

            # Add a subelement for each property.

            if property_type1 != current_property_type and property_type2 is not None:

                # Find abstract property types.

                property_types = self.get_property_types_for_uriref(property_type1)
                property_types.append(property_type1)

                # Create elements for each property.

                property_elements = []
                for property_type in property_types:
                    label = self.get_label(property_type)
                    if not property_labels1.has_key(label):
                        property_elements.append(item_element.appendChild(doc.createElement(label)))
                        property_labels1[label] = None

                # Remember the current property type and control the production
                # of attributes.

                current_property_type = property_type1
                property_labels2 = {}

            # Add properties as attributes to the property and item elements.

            if property_type2 is not None:
                self.fill_element_properties(doc, property_elements, property_type2, property_value, property_labels2)
            elif property_type1 is not None:
                self.fill_element_properties(doc, [item_element], property_type1, property_value)

    def fill_element_properties(self, doc, elements, property_type, property_value, labels=None):

        # Find abstract property types.

        property_types = self.get_property_types_for_uriref(property_type)
        property_types.append(property_type)

        # Set attributes for all property types.

        for property_type in property_types:

            # Get a simple label.

            label = self.get_label(property_type)
            if labels is not None:
                if labels.has_key(label):
                    continue
                labels[label] = property_value

            # Write property values to attributes.

            if isinstance(property_value, self.Literal):
                for element in elements:
                    element.setAttribute(label, unicode(property_value))

            # Write item types out nicely.

            elif label == "item-type":
                for element in elements:
                    element.setAttribute(label, self.get_label(property_value))

            # For URIRef-based properties, write identifiers out.

            else:
                for element in elements:
                    element.setAttribute(label, self.get_identifier_from_item(property_value))

    # Import/export methods.

    def parse_item(self, stream, item_type_name, uriref=None):

        """
        From the given 'stream', parse an item having the given 'item_type_name'
        and bearing the given 'uriref'.
        """

        handler = self.get_handler_for_item_type_name(item_type_name)
        if handler is None:
            return None
        try:
            if handler is not None:
                return handler.parse(stream, uriref=uriref)
        except handler.DuplicateResourceError, exc:
            raise self.DuplicateResourceError, exc

    def serialise_item(self, item, stream, *args, **kw):

        """
        Serialise the given 'item' to the given 'stream', specifying additional
        arguments to control the serialisation process.
        """

        handler = self.get_handler(item)
        if handler is not None:
            handler.write_to_stream(stream, main_node=item, *args, **kw)

    # Update methods.

    def add_item(self, item, item_type_name, doc):

        """
        Add an 'item' having the given 'item_type_name' to the store, using the
        definition document 'doc'. If 'item' is None, a new item will be added
        to the store.
        """

        doc_root = doc.xpath("item/*")[0]
        uriref = self.get_uriref(item)
        handler = self.get_handler_for_item_type_name(item_type_name)
        if handler is not None:
            handler.parse_document_fragment(doc, doc_root, uriref=uriref)

    def remove_item(self, item, deep=0):

        "Remove the given 'item' from the store."

        handler = self.get_handler(item)
        if handler is not None:
            handler.remove_node(item, deep)

    def has_item(self, item):

        "Return whether the store contains the given 'item'."

        return self.store.has_triple((item, None, None))

    # Conversions from items to identifiers and back again.

    def get_item_from_identifier(self, identifier):

        """
        Return an item built from the given 'identifier'. Here, we distinguish
        between BNode, URIRef within the store, and other URIRef items as
        follows:

        BNode                               starts with _
        URIRef within base URI for store    unprefixed (add the base URI)
        URIRef                              starts with -
        """

        if identifier.startswith("_"):
            return self.BNode(identifier)
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
        between BNode, URIRef within the store, and other URIRef items as
        follows:

        BNode                               starts with _
        URIRef within base URI for store    unprefixed (remove the base URI)
        URIRef                              starts with -
        """

        item_str = unicode(item)

        if isinstance(item, self.URIRef):
            # URIRef within base URI for store:
            if item_str.startswith(unicode(self.base_uri)):
                return item_str[len(unicode(self.base_uri)):]
            # Other URIRef:
            else:
                return "-" + item_str
        else:
            # BNodes should begin with _.
            return unicode(item)

    # Convenience methods.

    def get_label(self, uriref):

        "Return a label for a (typically) type-based 'uriref'."

        if uriref == self.TYPE:
            return "item-type"
        else:
            return uriref.split("/")[-1]

    def get_prefix(self, uriref, label):

        "Return the prefix for the 'uriref' minus the 'label'."

        return uriref[:-len(label)-1]

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

    def get_identifier_from_item_type(self, item_type):
        return self.get_label(item_type)

    def get_urirefs_from_identifier(self, identifier):

        """
        Return a list of URIRef objects corresponding to the given property type
        'identifier' or None if any URIRef objects should correspond (when
        'identifier' is specified as None).
        """

        if identifier == "item-type":
            return [self.TYPE]
        elif identifier is None:
            return None
        else:
            return self.get_urirefs_for_property_type(identifier)

    def get_item_types_from_identifiers(self, values):
        l = []
        for value in values:
            l += self.get_values_from_identifier(self.TYPE, value)
        return l

    def get_values_from_identifier(self, property_type, value):
        if value is None:
            return [None]
        elif property_type == self.TYPE:
            return self.get_urirefs_for_item_type(value)
        else:
            label = self.get_label(property_type)
            if label in ("related-to", "uri"):
                return [self.get_item_from_identifier(value)]
            else:
                return [self.Literal(value)]

    def get_values_using_predicates(self, predicates, value):
        property_types = predicates[-1]
        values = []
        for property_type in property_types:
            values += self.get_values_from_identifier(property_type, value)
        return values

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

    def combine_items(self, results):

        "Combine the 'results', returning a collection of items."

        return self.store.and_subjects(results)

    def get_items_using_attributes(self, attributes):

        """
        To query the store, prepare filters, taking information from the given
        'attributes' and adding the default item types where appropriate, and
        return a list of items.

        Supported attributes:

        filter-item-value, filter-type
        search-value, search-type, search-operation
        (attributes supported by get_date_from_attributes)
        """

        results = []

        # Use filtering categories.

        if attributes.has_key("filter-item-value"):

            predicates = self.get_predicates_for_attribute(attributes["filter-type"])

            filter_item_values = self.get_values_using_predicates(
                predicates,
                attributes["filter-item-value"]
                )

            # Ask the handlers for criteria.
            # Make a pattern requesting all suitable items.

            pattern = (None,) + \
                predicates + \
                (self.get_comparison(None, filter_item_values),)

            results.append(self.store.subjects(pattern=pattern))

        elif attributes.has_key("search-value"):

            predicates = self.get_predicates_for_attribute(attributes["search-type"])

            search_values = self.get_values_using_predicates(
                predicates,
                attributes["search-value"]
                )

            op = attributes.get("search-operation")

            # Ask the handlers for criteria.
            # Make a pattern requesting all suitable items.

            pattern = (None,) + \
                predicates + \
                (self.get_comparison(op, search_values),)

            results.append(self.store.subjects(pattern=pattern))

        # Date-based filtering.

        date = self.get_date_from_attributes(**attributes)
        if date is not None:

            # For date predicate restrictions try this:
            # self.store.Expression(
            #        "_ not in ?",
            #        [self.get_urirefs_for_property_type("created") + self.get_urirefs_for_property_type("last-modified")]
            #        )

            # Ask the handlers for datetime-related criteria.

            pattern = (
                None,
                None,
                self.get_urirefs_for_property_type("datetime"),
                self.get_comparison("startswith", [date])
                )

            results.append(self.store.subjects(pattern=pattern))

        # Or use type-based criteria.

        if attributes.has_key("item-type") and attributes["item-type"] != "all":
            item_types = [attributes["item-type"]]
        else:
            item_types = self.default_item_types

        # Ask the handlers for type-related criteria.

        pattern = (
            None,
            self.get_urirefs_from_identifier("item-type"),
            self.get_item_types_from_identifiers(item_types),
            )

        results.append(self.store.subjects(pattern=pattern))

        # Combine the results.

        return self.combine_items(results)

    def get_date_from_attributes(self, **attributes):

        "Return the date string for the given 'attributes'."

        if attributes.get("year") is not None:
            if attributes.get("month") is not None:
                if attributes.get("day") is not None:
                    return "%04d%02d%02d" % (attributes["year"], attributes["month"], attributes["day"])
                else:
                    return "%04d%02d" % (attributes["year"], attributes["month"])
            else:
                return "%04d" % attributes["year"]
        return None

def open(store, handlers, base_uri=None):

    """
    Open an RDFAccess store accessing the given 'store', using the given
    'handlers', and employing the given, optional 'base_uri'.
    """

    if not getattr(store, "supports_querying", 0):
        raise NotSupportedError, "Store does not support querying."

    if base_uri is not None:
        return Store(store, handlers, base_uri)
    else:
        return Store(store, handlers)

def unique(l):
    d = {}
    for i in l:
        d[i] = None
    return d.keys()

# vim: tabstop=4 expandtab shiftwidth=4
