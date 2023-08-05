#!/usr/bin/env python

"Utilities for importing and exporting khtml documents."

import libxml2dom

def import_doc(html_doc):

    """
    Import the given 'html_doc' into libxml2dom. Depending on the kind of the
    original document, the returned document will either have an empty namespace
    and use upper case element names (old-style HTML) or have a non-empty
    namespace and use lower case element names (XHTML and other document types).
    """

    # Create a placeholder document.

    doc = libxml2dom.createDocument(None, "HTML", None)
    doc_root = doc.xpath("HTML")[0]

    # Import the root node from khtml.

    for html_root in html_doc.childNodes:
        if html_root.localName.upper() == "HTML":
            imported_root = doc.importNode(html_root, 1)
            doc.replaceChild(imported_root, doc_root)

    return doc

def export_doc(html_doc, doc):

    """
    Copy into 'html_doc' the libxml2dom 'doc' whose root element is an HTML (or
    html) element.
    """

    # Find the root element.

    query = "*[local-name() = 'HTML']"
    doc_root = (doc.xpath(query) or doc.xpath(query.lower()))[0]

    # Replace the root element in the original khtml document.

    for html_root in html_doc.childNodes:
        if html_root.localName.upper() == "HTML":
            imported_root = html_doc.importNode(doc_root, 1)
            html_doc.replaceChild(imported_root, html_root)

# vim: tabstop=4 expandtab shiftwidth=4
