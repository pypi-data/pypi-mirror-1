#!/usr/bin/env python

"Make 'to do' lists from nested lists or documents."

import qtxmldom

def main(part):
    r = part.selection()
    if r.isNull():
        html_doc = qtxmldom.fromNode(part.document())

        # Get the first list element.

        list_elements = html_doc.getElementsByTagName("UL")

    else:
        html_doc = qtxmldom.fromNode(r.cloneContents())

        # Assume that we have the list highlighted and that the elements are the
        # child nodes of the fragment.

        list_elements = [html_doc]

    f = open("/tmp/xxx.txt", "w")
    for list_element in list_elements:
        title, to_do = get_list(list_element)
        print >>f, title, to_do
    f.close()

def get_list(list_element, title=None):
    list_element.normalize()

    to_do = []

    # At UL or equivalent element.
    # Expect LI elements defining list items.
    # Special case: text followed by UL elements produces a new list.

    for child_node in list_element.childNodes:

        # Set the title using text nodes.

        if title is None and child_node.nodeType == child_node.TEXT_NODE:
            title = child_node.nodeValue

        # Work out what to do with elements.

        elif child_node.nodeType == child_node.ELEMENT_NODE:

            # List items should be inspected for sublists.

            if child_node.localName == "LI":
                to_do.append(get_item(child_node))

            # Sublists should be visited.

            elif child_node.localName == "UL":
                return get_list(child_node, title=title)

    return title, to_do

def get_item(item_element):
    item_element.normalize()

    # Test for nested UL elements.

    sublists = item_element.getElementsByTagName("UL")

    # Simple items are returned.

    if len(sublists) == 0:
        return "".join([n.toUnicode() for n in item_element.childNodes]).strip()

    # Sublists are processed and returned.

    else:
        to_do_sub = []
        title = None
        for child_node in item_element.childNodes:

            # Set the title using text nodes.

            if child_node.nodeType == child_node.TEXT_NODE:
                title = child_node.nodeValue
            elif child_node.nodeType == child_node.ELEMENT_NODE and child_node.localName == "UL":
                to_do_sub.append(get_list(child_node, title=title))

        return to_do_sub

# vim: tabstop=4 expandtab shiftwidth=4
