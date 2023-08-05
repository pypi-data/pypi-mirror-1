#!/usr/bin/env python

"""
PyXML-style DOM API for qtxml and KHTML.

Copyright (C) 2005 Paul Boddie <paul@boddie.org.uk>

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
59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

--------

In the PyAutomation KPart, the following can be used to get a qtxmldom version
of the active document:

  import qtxmldom
  doc = fromNode(part.document())

If the module is edited, then the reload built-in function will probably update
the code, but the active DOM objects then need to be discarded.

With the KHTMLAutomation KPart active, the following can be used at a normal
Python prompt:

  doc = qtxmldom.fromRemoteObject(obj)

(Where obj has been obtained using the qtxmldom.remote module - see
examples/remote.py for more information.)
"""

import xml.dom

__version__ = "0.2.3"

class RemoteNode(object):

    "A representation of a remote object, accessed via DCOP."

    def __init__(self, obj, accessor):
        self.obj = obj
        self.accessor = accessor

    def __getattr__(self, name):
        return RemoteMethod(self.obj, self.accessor, name)

class RemoteMethod(object):

    """
    A wrapper around a remote method call, ensuring that the correct result is
    obtained.
    """

    def __init__(self, obj, accessor, name):
        import qt
        self.qt = qt
        self.obj = obj
        self.accessor = accessor
        self.name = name

    def _convert_obj(self, obj):
        if isinstance(obj, RemoteNode):
            return obj.obj
        else:
            return obj

    def __call__(self, *args):
        method = getattr(self.accessor, self.name)

        # Add the method's context and convert other arguments if appropriate.

        args = (self.obj,) + tuple(map(self._convert_obj, args))

        # Test the status.

        status, result_list = method(*args)
        if not status:
            raise RuntimeError, "Remote method '%s' failed for node '%s'" % (self.name, self.obj)

        if isinstance(result_list, self.qt.QStringList):
            result_type = result_list[0]
            result_value = result_list[1]
            if result_type == "string":
                return result_value
            else:
                return RemoteNode(result_value, self.accessor)
        else:
            return result_list

class Implementation(object):

    "Contains an abstraction over the DOM implementation."

    def createDocumentType(self, localName, publicId, systemId):
        return DocumentType(self._createDocumentType(localName, publicId,
            systemId), self)

    def _createDocumentType(self, localName, publicId, systemId):
        return self.impl.createDocumentType(
            self.make_string(localName), self.make_string(publicId),
            self.make_string(systemId)
            )

    def createDocument(self, namespaceURI, localName, doctype):
        if doctype is not None:
            _doctype = doctype._doctype
        else:
            _doctype = self._createDocumentType(localName, None, None)
        return Node(
            self.impl.createDocument(
                self.make_string(namespaceURI), self.make_string(localName),
                _doctype),
            self)

class khtmlRemoteImplementation(Implementation):

    def __init__(self, _impl=None):
        import qt
        self.qt = qt

    # Conversion methods.

    def convert(self, _node):
        return _node

    def make_string(self, s):

        # NOTE: Dubious conversion.

        if s is None:
            return self.qt.QString()
        else:
            return self.qt.QString(s)

    def get_string(self, s):
        return unicode(s)

class khtmlImplementation(Implementation):

    def __init__(self, _impl=None):
        import khtml
        self.khtml = khtml
        if _impl is not None:
            self.impl = _impl
        else:
            self.impl = khtml.DOM.DOMImplementation()

    # Conversion methods.

    def convert(self, _node):
        if _node.nodeType() == xml.dom.Node.ELEMENT_NODE:
            return self.khtml.DOM.Element(_node)
        elif _node.nodeType() == xml.dom.Node.ATTRIBUTE_NODE:
            return self.khtml.DOM.Attr(_node)
        elif _node.nodeType() == xml.dom.Node.DOCUMENT_NODE:
            return self.khtml.DOM.Document(_node)
        elif _node.nodeType() == xml.dom.Node.TEXT_NODE:
            return self.khtml.DOM.Text(_node)
        else:
            return _node

    def make_string(self, s):

        # NOTE: Dubious conversion.

        if s is None:
            return self.khtml.DOM.DOMString()
        else:
            return self.khtml.DOM.DOMString(s)

    def get_string(self, s):
        return unicode(s.string())

class qtxmlImplementation(Implementation):

    def __init__(self, _impl=None):
        import qtxml, qt
        self.qtxml = qtxml
        self.qt = qt
        if _impl is not None:
            self.impl = _impl
        else:
            self.impl = qtxml.QDomImplementation()

    # Conversion methods.

    def convert(self, _node):
        if _node.nodeType() == xml.dom.Node.ELEMENT_NODE:
            return _node.toElement()
        elif _node.nodeType() == xml.dom.Node.ATTRIBUTE_NODE:
            return _node.toAttr()
        elif _node.nodeType() == xml.dom.Node.DOCUMENT_NODE:
            return _node.toDocument()
        elif _node.nodeType() == xml.dom.Node.TEXT_NODE:
            return _node.toText()
        else:
            return _node

    def make_string(self, s):

        # NOTE: Dubious conversion.

        if s is None:
            return self.qt.QString()
        else:
            return s

    def get_string(self, s):
        return unicode(s)

class NodeList(object):

    "Represents lists of nodes in Python-like list objects."

    def __init__(self, _list, impl):

        """
        Initialise the list with the underlying '_list' and 'impl' - the
        DOM implementation in use.
        """

        self._list = _list
        self.impl = impl

    def __len__(self):
        return self._list.length()

    def __getitem__(self, i):

        "Get element 'i' from the list."

        if i >= 0 and i < self._list.length():
            _node = self._list.item(i)
        elif i < 0 and -i <= self._list.length():
            _node = self._list.item(self._list.length() + i)
        else:
            raise IndexError, i

        if _node.isNull():
            raise IndexError, i

        return Node(_node, self.impl)

    # __setitem__ not yet implemented.

    def __iter__(self):
        return NodeListIterator(self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[%s]" % ", ".join([repr(node) for node in self])

class NodeListIterator(object):
    def __init__(self, list):
        self.list = list
        self.index = 0

    def next(self):
        try:
            node = self.list[self.index]
            self.index += 1
            return node
        except IndexError:
            raise StopIteration

class NamedNodeMap(object):

    "Represents maps of names to nodes in Python-like dictionary objects."

    def __init__(self, _map, impl):

        """
        Initialise the dictionary with the underlying '_map' and 'impl' - the
        DOM implementation in use.
        """

        self._map = _map
        self.impl = impl

    def getNamedItem(self, name):
        _node = self._map.getNamedItem(self.impl.make_string(name))

        if _node.isNull():
            raise KeyError, name

        return Node(_node, self.impl)

    def getNamedItemNS(self, ns, localName):
        _node = self._map.getNamedItemNS(self.impl.make_string(ns), self.impl.make_string(localName))

        if _node.isNull():
            raise KeyError, name

        return Node(_node, self.impl)

    def setNamedItem(self, node):

        # NOTE: The identity of the supplied node if retrieved later is not
        # NOTE: guaranteed to be the same.

        _node = self._map.setNamedItem(node._node)

        if _node.isNull():
            raise ValueError, node

    def setNamedItemNS(self, node):

        # NOTE: The identity of the supplied node if retrieved later is not
        # NOTE: guaranteed to be the same.

        _node = self._map.setNamedItemNS(node._node)

        if _node.isNull():
            raise ValueError, node

    def __getitem__(self, name):
        return self.getNamedItem(name)

    def __setitem__(self, name, node):
        if name == node.nodeName:
            self.setNamedItem(node)
        else:
            raise KeyError, name

    def __delitem__(self, name):
        _node = self._map.removeNamedItem(self.impl.make_string(name))

        if _node.isNull():
            raise KeyError, name

    def values(self):
        l = []
        for i in range(0, self._map.length()):
            _node = self._map.item(i)
            if not _node.isNull():
                l.append(Node(_node, self.impl))
        return l

    def keys(self):
        return [(node.namespaceURI, node.localName) for node in self.values()]

    def items(self):
        return [((node.namespaceURI, node.localName), node) for node in self.values()]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{%s}" % ",\n".join(["%s : %s" % (repr(key), repr(value)) for key, value in self.items()])

class DocumentType(object):
    def __init__(self, _doctype, impl):
        self._doctype = _doctype
        self.impl = impl

    def _name(self):
        return self.impl.get_string(self._doctype.name())

    def _publicId(self):
        return self.impl.get_string(self._doctype.publicId())

    def _systemId(self):
        return self.impl.get_string(self._doctype.systemId())

    def _entities(self):
        return NamedNodeMap(self._doctype.entities(), self.impl)

    def _notations(self):
        return NamedNodeMap(self._doctype.notations(), self.impl)

    name = property(_name)
    publicId = property(_publicId)
    systemId = property(_systemId)
    entities = property(_entities)
    notations = property(_notations)

class Node(object):

    """
    Class representing all node types, although many methods will not be
    applicable to all such types.
    """

    ATTRIBUTE_NODE = xml.dom.Node.ATTRIBUTE_NODE
    COMMENT_NODE = xml.dom.Node.COMMENT_NODE
    DOCUMENT_NODE = xml.dom.Node.DOCUMENT_NODE
    DOCUMENT_TYPE_NODE = xml.dom.Node.DOCUMENT_TYPE_NODE
    ELEMENT_NODE = xml.dom.Node.ELEMENT_NODE
    ENTITY_NODE = xml.dom.Node.ENTITY_NODE
    ENTITY_REFERENCE_NODE = xml.dom.Node.ENTITY_REFERENCE_NODE
    NOTATION_NODE = xml.dom.Node.NOTATION_NODE
    PROCESSING_INSTRUCTION_NODE = xml.dom.Node.PROCESSING_INSTRUCTION_NODE
    TEXT_NODE = xml.dom.Node.TEXT_NODE

    def __init__(self, _node, impl):

        self.impl = impl

        # Do the necessary casting at the wrapper level.

        self._node = self.impl.convert(_node)

    def _doctype(self):
        if self.nodeType == self.DOCUMENT_NODE:
            return DocumentType(self._node.doctype(), self.impl)
        else:
            return None

    def _ownerElement(self):
        if self.nodeType == self.ATTRIBUTE_NODE:
            return Node(self._node.ownerElement(), self.impl)
        else:
            return None

    def _ownerDocument(self):
        if self.nodeType == self.DOCUMENT_NODE:
            return self
        else:
            return Node(self._node.ownerDocument(), self.impl)

    def _childNodes(self):
        return NodeList(self._node.childNodes(), self.impl)

    def _nodeValue(self):
        return self.impl.get_string(self._node.nodeValue())

    def _nodeName(self):
        return self.impl.get_string(self._node.nodeName())

    def _tagName(self):
        return self.impl.get_string(self._node.tagName())

    def _namespaceURI(self):
        return self.impl.get_string(self._node.namespaceURI())

    def _prefix(self):
        return self.impl.get_string(self._node.prefix())

    def _localName(self):
        # NOTE: Work around strange behaviour.
        s = self.impl.get_string(self._node.localName())
        if not s:
            return self._nodeName()
        return s

    def _parentNode(self):
        if self.nodeType == self.DOCUMENT_NODE:
            return None
        else:
            return Node(self._node.parentNode(), self.impl)

    def _nodeType(self):
        return self._node.nodeType()

    def _attributes(self):
        return NamedNodeMap(self._node.attributes(), self.impl)

    def getAttributeNS(self, ns, localName):
        if hasattr(self._node, "getAttributeNS"):
            return self.impl.get_string(self._node.getAttributeNS(self.impl.make_string(ns), self.impl.make_string(localName)))
        else:
            return self.impl.get_string(self._node.attributeNS(self.impl.make_string(ns), self.impl.make_string(localName)))

    def getAttribute(self, name):
        if hasattr(self._node, "getAttribute"):
            return self.impl.get_string(self._node.getAttribute(self.impl.make_string(name)))
        else:
            return self.impl.get_string(self._node.attribute(self.impl.make_string(name)))

    def getAttributeNodeNS(self, ns, localName):
        if hasattr(self._node, "getAttributeNodeNS"):
            return Node(self._node.getAttributeNodeNS(self.impl.make_string(ns), self.impl.make_string(localName)), self.impl)
        else:
            return Node(self._node.attributeNodeNS(self.impl.make_string(ns), self.impl.make_string(localName)), self.impl)

    def getAttributeNode(self, name):
        if hasattr(self._node, "getAttributeNode"):
            return Node(self._node.getAttributeNode(self.impl.make_string(name)), self.impl)
        else:
            return Node(self._node.attributeNode(self.impl.make_string(name)), self.impl)

    def hasAttributeNS(self, ns, name):
        return self._node.hasAttributeNS(self.impl.make_string(ns), self.impl.make_string(name))

    def hasAttribute(self, name):
        return self._node.hasAttribute(self.impl.make_string(name))

    def setAttributeNS(self, ns, name, value):
        self._node.setAttributeNS(self.impl.make_string(ns), self.impl.make_string(name), self.impl.make_string(value))

    def setAttribute(self, name, value):
        self._node.setAttribute(self.impl.make_string(name), self.impl.make_string(value))

    def setAttributeNodeNS(self, ns, name, node):
        self._node.setAttributeNodeNS(node._node)

    def setAttributeNode(self, name, node):
        self._node.setAttributeNode(node._node)

    def createElementNS(self, ns, name):
        return Node(self._node.createElementNS(self.impl.make_string(ns), self.impl.make_string(name)), self.impl)

    def createElement(self, name):
        return Node(self._node.createElement(self.impl.make_string(name)), self.impl)

    def createAttributeNS(self, ns, name):
        return Node(self._node.createAttributeNS(self.impl.make_string(ns), self.impl.make_string(name)), self.impl)

    def createAttribute(self, name):
        return Node(self._node.createAttribute(self.impl.make_string(name)), self.impl)

    def createTextNode(self, value):
        return Node(self._node.createTextNode(self.impl.make_string(value)), self.impl)

    def importNode(self, node, deep):

        if node.nodeType == self.ELEMENT_NODE:
            imported_element = self.ownerDocument.createElementNS(node.namespaceURI, node.tagName)
            for value in node.attributes.values():
                imported_element.setAttributeNS(value.namespaceURI, value.nodeName, value.nodeValue)

            if deep:
                for child in node.childNodes:
                    imported_child = self.importNode(child, deep)

                    # NOTE: Don't upset KHTML with empty text nodes.
                    # NOTE: Apparently, we would handle a DOMException, but
                    # NOTE: KHTML just crashes instead.

                    if imported_child:
                        imported_element.appendChild(imported_child)

            return imported_element

        elif node.nodeType == self.TEXT_NODE:

            # NOTE: Don't upset KHTML with empty text nodes.

            if len(node.nodeValue.strip()) == 0:
                return None

            return self.ownerDocument.createTextNode(node.nodeValue)

        elif node.nodeType == self.ATTRIBUTE_NODE:
            return self.ownerDocument.createAttributeNS(node.namespaceURI, node.name)

        raise ValueError, node.nodeType

    def insertBefore(self, newNode, oldNode):
        return Node(self._node.insertBefore(newNode._node, oldNode._node), self.impl)

    def replaceChild(self, newNode, oldNode):
        return Node(self._node.replaceChild(newNode._node, oldNode._node), self.impl)

    def appendChild(self, node):
        return Node(self._node.appendChild(node._node), self.impl)

    def getElementsByTagName(self, tagName):
        if hasattr(self._node, "getElementsByTagName"):
            return NodeList(self._node.getElementsByTagName(self.impl.make_string(tagName)), self.impl)
        else:
            return NodeList(self._node.elementsByTagName(self.impl.make_string(tagName)), self.impl)

    def getElementsByTagNameNS(self, namespaceURI, localName):
        if hasattr(self._node, "getElementsByTagNameNS"):
            return NodeList(self._node.getElementsByTagNameNS(self.impl.make_string(namespaceURI), self.impl.make_string(localName)), self.impl)
        else:
            return NodeList(self._node.elementsByTagNameNS(self.impl.make_string(namespaceURI), self.impl.make_string(localName)), self.impl)

    def normalize(self):
        self._node.normalize()

    doctype = property(_doctype)
    ownerElement = property(_ownerElement)
    ownerDocument = property(_ownerDocument)
    childNodes = property(_childNodes)
    value = data = nodeValue = property(_nodeValue)
    name = nodeName = property(_nodeName)
    tagName = property(_tagName)
    namespaceURI = property(_namespaceURI)
    prefix = property(_prefix)
    localName = property(_localName)
    parentNode = property(_parentNode)
    nodeType = property(_nodeType)
    attributes = property(_attributes)

    def isSameNode(self, other):
        return self._node is other._node

    def __eq__(self, other):
        return self._node is other._node

    def toUnicode(self):
        if hasattr(self._node, "toString"):
            return self.impl.get_string(self._node.toString())
        elif hasattr(self._node, "toHTML"):
            # Using qtxml implementation since toHTML returns a QString.
            return qtxmlImplementation().get_string(self._node.toHTML())
        else:
            # NOTE: Verify encodings!

            import qt
            byte_array = qt.QByteArray()
            ostream = qt.QTextOStream(byte_array)
            ostream.setEncoding(qt.QTextStream.Unicode)
            self._node.save(ostream, 2)
            istream = qt.QTextIStream(byte_array)
            istream.setEncoding(qt.QTextStream.Unicode)
            return unicode(istream.read())

    def toString(self, encoding="utf-8"):
        return self.toUnicode().encode(encoding)

# Convenience functions.

def getRemoteDocument(remote_object):

    """
    Get a KHTML-style node for the given 'remote_object'. Use the
    qtxmldom.remote module to find suitable objects to use with this function.
    """

    status, result = remote_object.getDocument()
    if not status:
        raise RuntimeError, "No remote document found for %s" % repr(remote_object)

    try:
        doc = result[1]
        return getRemoteNode(doc, remote_object)
    except IndexError:
        raise RuntimeError, "No remote document found for %s" % repr(remote_object)

def getRemoteNode(node, remote_object):

    """
    Get a KHTML-style node for the given 'node' accessed via the supplied
    'remote_object'. Use the qtxmldom.remote module to find suitable objects to
    use with this function.
    """

    return RemoteNode(node, remote_object)

def fromRemoteObject(remote_object):

    "Return a PyXML-style DOM for the given 'remote_object'."

    return Node(getRemoteDocument(remote_object), khtmlRemoteImplementation())

def fromRemoteNode(node):

    "Return a PyXML-style DOM for the given remote 'node'."

    return Node(node, khtmlRemoteImplementation())

def fromNode(node):

    "Return a PyXML-style DOM for the given KHTML 'node'."

    return Node(node, khtmlImplementation())

def fromQDomNode(node):

    "Return a PyXML-style DOM for the given qtxml 'node'."

    return Node(node, qtxmlImplementation())

def parse(stream_or_string):

    """
    Parse the given 'stream_or_string', where the supplied object can either be
    a stream (such as a file or stream object), or a string (containing the
    filename of a document).

    A document object is returned by this function.
    """

    if hasattr(stream_or_string, "read"):
        stream = stream_or_string
        return parseString(stream.read())
    else:
        return parseFile(stream_or_string)

def parseFile(filename):

    """
    Parse the file having the given 'filename'.

    A document object is returned by this function.
    """

    import qt, qtxml
    f = qt.QFile(filename)
    try:
        d = qtxml.QDomDocument()
        if d.setContent(f)[0]:
            return fromQDomNode(d)
        else:
            raise IOError, filename
    finally:
        f.close()

def parseString(s):

    """
    Parse the content of the given string 's'.

    A document object is returned by this function.
    """

    import qtxml
    d = qtxml.QDomDocument()
    if d.setContent(s)[0]:
        return fromQDomNode(d)
    else:
        raise IOError, s

# vim: tabstop=4 expandtab shiftwidth=4
