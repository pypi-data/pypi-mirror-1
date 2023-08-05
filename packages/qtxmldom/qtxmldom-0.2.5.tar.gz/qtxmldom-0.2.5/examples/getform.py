#!/usr/bin/env python

"Extract form information using XSLTools."

import sys
sys.path.append("/home/paulb/Software/Python/libxml2dom")
sys.path.append("/home/paulb/Software/Python/XSLTools")
import XSLForms.Fields
import qtxmldom
from qtxmldom.khtmlutils import import_doc, export_doc

def main(part):
    html_doc = qtxmldom.fromNode(part.document())
    doc = import_doc(html_doc)
    query = "/h:HTML/h:BODY//h:INPUT|//h:HTML/h:BODY//h:SELECT"
    raw_fields = doc.xpath(query, namespaces={"h" : ""}) or doc.xpath(query.lower(), namespaces={"h" : "http://www.w3.org/1999/xhtml"})
    query = "/h:HTML/h:BODY//h:TEXTAREA"
    raw_texts = doc.xpath(query, namespaces={"h" : ""}) or doc.xpath(query.lower(), namespaces={"h" : "http://www.w3.org/1999/xhtml"})
    parameters = {}
    for raw_field in raw_fields:
        parameters[raw_field.getAttribute("name")] = raw_field.getAttribute("value") or ""
    print parameters
    for raw_text in raw_texts:
        parameters[raw_text.getAttribute("name")] = "".join([n.nodeValue for n in raw_text.xpath("text()")])
    print parameters
    fields = XSLForms.Fields.Fields()
    documents = fields.make_documents(parameters.items())
    for name, document in documents.items():
        print document.toString()
    export_doc(html_doc, doc)

# vim: tabstop=4 expandtab shiftwidth=4
