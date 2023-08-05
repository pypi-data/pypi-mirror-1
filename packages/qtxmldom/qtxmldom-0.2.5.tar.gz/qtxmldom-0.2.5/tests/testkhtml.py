#!/usr/bin/env python

from khtml import KHTMLPart
from kdeui import KMainWindow
from qt import QVBox

class HTMLPart(KHTMLPart):
    def __init__(self, qvbox):
        KHTMLPart.__init__(self, qvbox)

class HTMLWindow(KMainWindow):
    def __init__(self):
        KMainWindow.__init__(self)
        self.vbox = QVBox(self)
        self.setCentralWidget(self.vbox)
        self.htmlpart = HTMLPart(self.vbox)

if __name__ == "__main__":

    from qtxmldom import fromNode
    from kdecore import KApplication
    import sys
    from xml.dom.minidom import parse
    from xml.dom.ext import PrettyPrint
    import xml.xpath

    if len(sys.argv) < 2:
        print "test.py <filename>"
        sys.exit(1)

    app = KApplication(sys.argv[1:], "Test")
    main = HTMLWindow()
    main.show()
    main.resize(512, 512)
    app.setMainWidget(main)

    # Set up the widget.

    main.htmlpart.begin()
    main.htmlpart.write("<html/>")
    main.htmlpart.end()

    # KHTML used to get upset if we tried to replace the root element or import
    # a head element.

    doc = parse(sys.argv[1])
    head = xml.xpath.Evaluate("/html/head", doc)[0]
    body = xml.xpath.Evaluate("/html/body", doc)[0]

    htmldoc = fromNode(main.htmlpart.document())

    try:
        print "Importing..."
        new_head = htmldoc.importNode(head, 1)
        new_body = htmldoc.importNode(body, 1)
        print "Imported"
        html = xml.xpath.Evaluate("/html", htmldoc)[0]
        print "Appending..."
        html.appendChild(new_head)
        html.appendChild(new_body)

    except IndexError:
        print "No document found."

    print "Imported document:"
    PrettyPrint(htmldoc)

    print "Select element:"
    select = xml.xpath.Evaluate("/html/body/form/select", htmldoc)[0]
    print select.tagName
    print "->", select.value, select.length

    app.exec_loop()
    sys.exit()

# vim: tabstop=4 expandtab shiftwidth=4
