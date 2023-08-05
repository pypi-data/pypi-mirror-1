#
# genxmlif, Release 0.7
# file: xmlifElementTree.py
#
# XML interface class to elementtree toolkit by Fredrik Lundh
#
# history:
# 2005-04-25 rl   created
#
# Copyright (c) 2005-2006 by Roland Leuthe.  All rights reserved.
#
# --------------------------------------------------------------------
# The generic XML interface is
#
# Copyright (c) 2005-2006 by Roland Leuthe
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# and will comply with the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# the author not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------


import string
import urllib
from types                      import TupleType
from elementtree.ElementTree    import *
from elementtree.XMLTreeBuilder import FancyTreeBuilder, TreeBuilder
from xmlifUtils                 import NsNameTupleFactory, convertToAbsUrl, processWhitespaceAction
from xmlifbase                  import XmlInterfaceBase, TreeWrapperBase, ElementWrapperBase, XmlIfBuilderExtensionBase

XML_NAMESPACE   = "http://www.w3.org/XML/1998/namespace"

#########################################################
# Derived interface class for elementtree toolkit

class XmlInterfaceElementTree (XmlInterfaceBase):
    #####################################################
    # for description of the interface methods see xmlifbase.py
    #####################################################

    def __init__ (self, verbose):
        XmlInterfaceBase.__init__ (self, verbose)
        self.treeWrapper    = TreeWrapperElementTree
        self.elementWrapper = ElementWrapperElementTree
        if self.verbose:
            print "Using elementtree interface module..."


    def createXmlTree (self, namespace, xmlRootTagName, publicId=None, systemId=None):
        rootNode = Element(xmlRootTagName)
        tree = ElementTree(rootNode)
        treeWrapperInst = TreeWrapperElementTree(self, tree)
        treeWrapperInst.getRootNode()._initElement ({}, []) # TODO: namespace handling
        return treeWrapperInst


    def parse (self, file, baseUrl="", ownerDoc=None):
        absUrl = convertToAbsUrl (file, baseUrl)
        fp     = urllib.urlopen (absUrl)
        try:
            tree = ElementTree()
            parser = ExtXMLTreeBuilder(file, absUrl)
            tree.parse(fp, parser)
        finally:
            fp.close()

        return TreeWrapperElementTree(self, tree)


    def parseString (self, text, ownerDoc=None):
        parser = ExtXMLTreeBuilder("", "", "")
        parser.feed(text)
        return TreeWrapper (self, ElementTree(parser.close()))


    def splitQName (self, qName):
        namespaceEndIndex = string.find (qName, '}')
        if namespaceEndIndex != -1:
            prefix     = qName[1:namespaceEndIndex]
            localName  = qName[namespaceEndIndex+1:]
        else:
            namespaceEndIndex = string.find (qName, ':')
            if namespaceEndIndex != -1:
                prefix     = qName[:namespaceEndIndex]
                localName  = qName[namespaceEndIndex+1:]
            else:
                prefix     = None
                localName  = qName
        return prefix, localName


    def toQName (self, tupleOrLocalName):
        if isinstance(tupleOrLocalName, TupleType):
            if tupleOrLocalName[0] != None:
                return "{%s}%s" %(tupleOrLocalName[0], tupleOrLocalName[1])
            else:
                return tupleOrLocalName[1]
        else:
            return tupleOrLocalName


#########################################################
# Wrapper class for ElementTree class

class TreeWrapperElementTree (TreeWrapperBase):

    def getRootNode (self):
        return self.xmlIf.elementWrapper(self.xmlIf, self, self.tree.getroot())


    def insertSubtree (self, nextSiblingWrapper, subTreeWrapper):
        if nextSiblingWrapper != None:
            insertIndex = self.tree.getroot().getchildren().index (nextSiblingWrapper.element)
        else:
            insertIndex = 0
        elementWrapperList = subTreeWrapper.getRootNode().getChildren()
        elementWrapperList.reverse()
        for elementWrapper in elementWrapperList:
            self.tree.getroot().insert (insertIndex, elementWrapper.element)


    def _createElement (self, tupleOrLocalName):
        if not isinstance(tupleOrLocalName, TupleType):
            elementNode = Element (tupleOrLocalName)
        else:
            raise NotImplementedError
        return elementNode


#########################################################
# Wrapper class for Element class

class ElementWrapperElementTree (ElementWrapperBase):

    def getTagName (self):
        return self.element.tag


    def getNamespaceURI (self):
        prefix, localName = self.xmlIf.splitQName(self.element.tag)
        return prefix


    def getParentNode (self):
        return self.__class__(self.xmlIf, self.treeWrapper, self.element.xmlIfExtDict["parentNode"])


    def getChildren (self, filterTag=None):
        if filterTag in (None, '*'):
            children = self.element.getchildren()
        else:
            children = self.element.findall(filterTag)

        return map(lambda element: self.__class__(self.xmlIf, self.treeWrapper, element), children)


    def getChildrenNS (self, namespaceURI, filterTag=None):
        if filterTag not in [None, "*"] and namespaceURI != None:
            filterTag = "{%s}%s" %(namespaceURI, filterTag)
        return ElementWrapperBase.getChildrenNS (self, namespaceURI, filterTag)


    def getFirstChild (self, filterTag=None):
        # replace base method (performance optimized)
        if filterTag in (None, '*'):
            children = self.element.getchildren()
            if children != []:
                element = children[0]
            else:
                element = None
        else:
            element = self.element.find(filterTag)

        if element != None:
            return self.__class__(self.xmlIf, self.treeWrapper, element)
        else:
            return None


    def getFirstChildNS (self, namespaceURI, filterTag=None):
        if filterTag not in [None, "*"] and namespaceURI != None:
            filterTag = "{%s}%s" %(namespaceURI, filterTag)
        return ElementWrapperBase.getFirstChild (self, filterTag)


    def getElementsByTagName (self, filterTag=None):
        if filterTag == '*':
            filterTag = None
        elements = self.element.getiterator (filterTag)

        return map(lambda element: self.__class__(self.xmlIf, self.treeWrapper, element), elements)


    def getElementsByTagNameNS (self, namespaceURI, filterTag=None):
        if filterTag not in [None, "*"] and namespaceURI != None:
            filterTag = "{%s}%s" %(namespaceURI, filterTag)
        return ElementWrapperBase.getElementsByTagNameNS (self, namespaceURI, filterTag)


    def appendChild (self, tupleOrLocalName, attributeDict={}):
        childElementWrapper = self._createElement (tupleOrLocalName, attributeDict)
        self.element.append (childElementWrapper.element)
        return childElementWrapper


    def insertBefore (self, tupleOrLocalName, refChild, attributeDict={}):
        childElementWrapper = self._createElement (tupleOrLocalName, attributeDict)
        if refChild == None:
            self.element.append (childElementWrapper.element)
        else:
            children = self.element.getchildren()
            self.element.insert (children.index(refChild.element), childElementWrapper.element)
        return childElementWrapper


    def removeChild (self, childElementWrapper):
        self.element.remove (childElementWrapper.element)


    def getAttributeDict (self):
        attrDict = {}
        for attrName, attrValue in self.element.attrib.items():
            attrDict[NsNameTupleFactory(self.xmlIf.splitQName(attrName))] = attrValue
        return attrDict


    def getAttribute (self, tupleOrAttrName):
        qName = self.xmlIf.toQName(tupleOrAttrName)
        if self.element.attrib.has_key(qName):
            return self.element.attrib[qName]
        else:
            return None


    def getLocalAttributeDirect (self, attrName):
        return self.element.attrib[attrName]


    def hasAttribute (self, tupleOrAttrName):
        return self.element.attrib.has_key(self.xmlIf.toQName(tupleOrAttrName))


    def setAttribute (self, tupleOrAttrName, attributeValue):
        if not self.hasAttribute (tupleOrAttrName):
            self.element.xmlIfExtDict["attributeSequence"].append(tupleOrAttrName)

        self.element.attrib[self.xmlIf.toQName(tupleOrAttrName)] = attributeValue


    def getElementValue (self):
        elementValueList = ["",]
        if self.element.text != None:
            elementValueList.append(self.element.text)
        for child in self.getChildren():
            if child.element.tail != None:
                elementValueList.append(child.element.tail)
        return string.join (elementValueList, "")


    def setElementValue (self, elementValue):
        self.element.text = elementValue
        for child in self.getChildren():
            child.element.tail = None
            

    def processWsElementValue (self, wsAction):
        if self.element.text != None:
            self.element.text = processWhitespaceAction (self.element.text, wsAction)
        for child in self.getChildren():
            if child.element.tail != None:
                child.element.tail = processWhitespaceAction (child.element.tail, wsAction)



########################################
# minixsv builder extension class
#

class XmlIfBuilderExtensionElementTree (XmlIfBuilderExtensionBase):
    
    def _getBaseUrl (self, curNode):
        qNameBaseAttr = "{%s}%s" %(XML_NAMESPACE, "base")
        if curNode.attrib.has_key(qNameBaseAttr):
            return convertToAbsUrl (curNode.attrib[qNameBaseAttr], self.baseUrlStack[0])
        else:
            return self.baseUrlStack[0]


###################################################
# Element tree builder class derived from XMLTreeBuilder
# extended to store related line numbers in the Element object

class ExtXMLTreeBuilder (FancyTreeBuilder, XmlIfBuilderExtensionElementTree):
    def __init__(self, filePath, absUrl):
        FancyTreeBuilder.__init__(self)
        XmlIfBuilderExtensionElementTree.__init__(self, filePath, absUrl)


    def _start_list(self, tag, attrib_in):
        elem = TreeBuilder._start_list(self, tag, attrib_in)
        self.start(elem, attrib_in)


    def start(self, element, attributes):
        XmlIfBuilderExtensionElementTree.startElementHandler (self, element, self._parser.ErrorLineNumber, self.namespaces[:], attributes)
        if len(self._target._elem) > 1:
            element.xmlIfExtDict["parentNode"] = self._target._elem[-2]
        else:
            element.xmlIfExtDict["parentNode"] = None


    def end(self, element):
        XmlIfBuilderExtensionElementTree.endElementHandler (self, element, self._parser.ErrorLineNumber)

