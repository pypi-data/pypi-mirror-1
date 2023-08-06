# File: xmlwriter.py
#
# Copyright (c) 2007 by Bibliotheca Hertziana -
#    Max Planck Institute for Art History, Rome, Italy
#
# German Free Software License (D-FSL)
#
# This Program may be used by anyone in accordance with the terms of the 
# German Free Software License
# The License may be obtained under <http://www.d-fsl.org>.
#

__author__ = """\
Jens Klein <jens@bluedynamics.com>, 
Martin Raspe <hertzhaft@biblhertz.it>"""
__docformat__ = 'plaintext'

import string
from elementtree.ElementTree import ElementTree
from elementtree.ElementTree import Comment
from elementtree.ElementTree import ProcessingInstruction
from StringIO import StringIO

class XMLWriter(object):
    """
    A modification of the _write method of ElementTree
    which supports namespaces in a reasonable way
    """
    default_namespaces = {"http://www.w3.org/XML/1998/namespace": "xml"}
    
    def __init__(self, tree, namespaces=None, encoding="utf-8"):
        self.tree = tree
        self.encoding = encoding
        self.setupDeclaredNamespaces(namespaces)
        
    def __call__(self, file=None, tree=None, namespaces=None, encoding=None):
        """
        namespace-aware serialization of a XML elementtree
        """
        if tree is not None:
            self.tree = tree
        if namespaces is not None:
            self.setupDeclaredNamespaces(namespaces)
        if encoding is not None:
            self.encoding = encoding
        if file is None:
            file = StringIO()
        if not hasattr(file, "write"):
            file = open(file, "wb")
        self.file = file
        assert isinstance(self.tree, ElementTree)
        assert self.tree._root is not None
        root = self.tree._root
        ns = self.declared_namespaces.copy() 
        # need a copy here, because original must stay intact 
        self.writeXMLHeader()
        self.write(root, ns)
        if isinstance(self.file, StringIO):
            return self.file.getvalue()

    def escapeText(self, text):
        text = self.encode(text)
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return text

    def escapeAttr(self, text):
        return self.escapeText(text).replace('"', '&quot;')

    def encode(self, text):
        if isinstance(text, unicode):
            return text.encode(self.encoding)
        elif isinstance(text, str):
            return text
        raise TypeError, 'XMLWriter: Cannot encode objects of type %s' % type(text)
        
    def cdata(self, text):
        if text.find("]]>") >= 0:
            raise ValueError("']]>' not allowed in a CDATA section")
        return "<![CDATA[%s]]>" % text

    def writeXMLHeader(self):
        self.file.write('<?xml version="1.0" encoding="%s"?>\n' % self.encoding)

    def writeAttr(self, name, value):
        self.file.write(" %s=\"%s\"" % (self.encode(name), self.escapeAttr(value)))

    def writeStartTagOpen(self, name):
        self.file.write("<%s" % self.encode(name))

    def writeStartTagClose(self):
        self.file.write(">")

    def writeContent(self, text):
        self.file.write(self.escapeText(text))

    def writeEmptyTagClose(self):
        self.file.write(" />")

    def writeEndTag(self, name):
        self.file.write("</%s>" % self.encode(name))

    def writeComment(self, node):
        self.file.write("<!-- %s -->" % self.escapeText(node.text))

    def writePI(self, node):
        self.file.write("<?%s?>" % self.escapeText(node.text))

    def setupDeclaredNamespaces(self, namespaces):
        """
        set up predeclared namespace declarations
        """
        self.xmlns_namespace = ''
        self.declared_namespaces = {}
        if not namespaces is None: 
            self.declared_namespaces = namespaces
        self.namespaces_by_prefix = {}
        self.prefixes = []
        ns_uris = self.declared_namespaces.keys()
        for uri in ns_uris:
            prefix = namespaces[uri]
            assert prefix not in self.prefixes
            self.prefixes.append(prefix)
            self.namespaces_by_prefix[prefix] = uri
        self.prefixes.sort()
        
    def getNamespaceByPrefix(self, prefix):
        return self.namespaces_by_prefix[prefix]

    def getXMLNS(self, prefix, namespace_uri):
        """
        return a "xmlns"-prefixed namespace declaration
        """
        if prefix == '':
            # unprefixed namespace ("xmlns" attribute)
            return ("xmlns", namespace_uri)
        else:
            # prefixed namespace ("xmlns:xy=" attribute)
            return ("xmlns:%s" % prefix, namespace_uri)

    def addPrefix(self, name, namespaces, attr=True):
        """
        given a decorated name (of the form {uri}tag), 
        return prefixed name and namespace declaration
        """
        if not name[:1] == "{":
            # no Namespace
            return name, None
        namespace_uri, name = string.split(name[1:], "}", 1)
        prefix = namespaces.get(namespace_uri, None)
        if prefix is None:
            # test for "xml" namespace
            prefix = self.default_namespaces.get(namespace_uri, None)
        if prefix is None:
            if attr:
                # namespaced attributes always need to be prefixed
                # (even if they are in the default namespace)
                prefix = "ns%d" % len(namespaces)
            else:
                # make this the default namespace (for tags)
                prefix = ''
        if prefix == '':
            # tag names remain unchanged
            if attr:
                # namespaced attributes always need to be prefixed
                # (even if they are in the default namespace)
                prefix = "ns%d" % len(namespaces)
                name = "%s:%s" % (prefix, name)
            else:
                if not namespace_uri == self.xmlns_namespace:
                # we redefine the namespace for the empty prefix
                    if namespaces.has_key(self.xmlns_namespace):
                        del namespaces[self.xmlns_namespace]
                    self.xmlns_namespace = namespace_uri
        else:
            # set prefix to name
            name = "%s:%s" % (prefix, name)
        if self.default_namespaces.get(namespace_uri, None) == prefix:
            # XML namespace etc., needs no declaration
            return name, None
        if namespaces.get(namespace_uri, None) == prefix:
            # namespace has already been declared before
            return name, None
        # get the appropriate declarations
        xmlns = self.getXMLNS(prefix, namespace_uri)
        namespaces[namespace_uri] = prefix
        return name, xmlns

    def write(self, node, namespaces):
        # write XML to file
        tag = node.tag
        if tag is Comment:
            # comments are not parsed by ElementTree!
            self.writeComment(node)
        elif tag is ProcessingInstruction:
            # PI's are not parsed by ElementTree!
            self.writePI(node)
        else:
            xmlns_items = [] # collects new namespaces in this scope
            attributes = node.items()
            for attrname, value in attributes:
                # (the elementtree parser discards these attributes)
                if attrname.startswith('xmlns:'):
                    namespaces[value] = attrname[6:]
                if attrname == "xmlns":
                    namespaces[value] = ''
            # get namespace for tag
            tag, xmlns = self.addPrefix(tag, namespaces, attr=False)
            # insert all declared namespaces into the root element
            if node == self.tree._root:
                for prefix in self.prefixes:
                    decl = self.getXMLNS(prefix, self.getNamespaceByPrefix(prefix))
                    if not prefix == '':
                        xmlns_items.append(decl)
                    else:
                        # a prefixless namespace has been declared
                        if node.tag.startswith("{"):
                            # insert the declaration only if root has a namespace
                            xmlns_items.append(decl)
                            if xmlns and xmlns[1] == decl[1]:
                                # root has the same namespace, so don't redeclare it
                                xmlns = None
            if xmlns:
                xmlns_items.append(xmlns)
            self.writeStartTagOpen(tag)
            # write attribute nodes
            for attrname, value in attributes:
                attrname, xmlns = self.addPrefix(attrname, namespaces)
                if xmlns:
                    xmlns_items.append(xmlns)
                self.writeAttr(attrname, value)
            # write collected xmlns attributes
            for attrname, value in xmlns_items:
                self.writeAttr(attrname, value)
            if node.text or len(node):
                self.writeStartTagClose()
                if node.text:
                    self.writeContent(node.text)
                for n in node:
                    self.write(n, namespaces.copy())
                self.writeEndTag(tag)
            else:
                self.writeEmptyTagClose()
            # for attrname, value in xmlns_items:
            #    del namespaces[value]
        if node.tail:
            self.writeContent(node.tail)

if __name__ == '__main__':
    from tests import test_suite
    suite = test_suite()
    unittest.TextTestRunner().run(suite)
