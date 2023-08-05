#!/usr/bin/env python

if __name__ == "__main__":

    from qtxmldom import qtxmlImplementation
    from xml.dom.ext import PrettyPrint
    import xml.xpath

    doc = qtxmlImplementation().createDocument(None, "horse", None)
    doc_root = xml.xpath.Evaluate("*", doc)[0]
    doc_root.setAttribute("name", "Simon")
    PrettyPrint(doc)

"""
    import sys
    from xml.dom.minidom import parse

    if len(sys.argv) < 2:
        print "test.py <filename>"
        sys.exit(1)

    doc = parse(sys.argv[1])
    doc_root = xml.xpath.Evaluate("*", doc)[0]
    qtdoc = Node(qtxml.QDomDocument(), qtxmlImplementation())

    try:
        print "Importing..."
        new_root = qtdoc.importNode(doc_root, 1)
        print "Imported"
        print "Appending..."
        qtdoc.appendChild(new_root)

    except IndexError:
        print "No document found."

    print "Imported document:"
    PrettyPrint(qtdoc)

    sys.exit()
"""

# vim: tabstop=4 expandtab shiftwidth=4
