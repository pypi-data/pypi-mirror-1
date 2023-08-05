#!/usr/bin/env python

"Convert text nodes to upper case."

import sys
sys.path.append("/home/paulb/Software/Python/libxml2dom")
import qtxmldom
from qtxmldom.khtmlutils import import_doc, export_doc

def main(part):
    html_doc = qtxmldom.Node(part.document(), qtxmldom.khtmlImplementation())
    doc = import_doc(html_doc)
    query = "/h:HTML/h:BODY//text()"
    text = doc.xpath(query, namespaces={"h" : ""}) or doc.xpath(query.lower(), namespaces={"h" : "http://www.w3.org/1999/xhtml"})
    for node in text:
        node.nodeValue = node.nodeValue.upper()
    export_doc(html_doc, doc)

# vim: tabstop=4 expandtab shiftwidth=4
