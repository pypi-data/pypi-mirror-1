#
# minixsv, Release 0.7
# file: pyxsval.py
#
# API for XML schema validator
#
# history:
# 2004-09-09 rl   created
# 2004-09-29 rl   adapted to re-designed XML interface classes,
#                 ErrorHandler separated, URL processing added, some bugs fixed
# 2004-10-07 rl   Validator classes extracted into separate files
# 2004-10-12 rl   API re-worked, XML text processing added
#
# Copyright (c) 2004-2006 by Roland Leuthe.  All rights reserved.
#
# --------------------------------------------------------------------
# The minixsv XML schema validator is
#
# Copyright (c) 2004-2006 by Roland Leuthe
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

__all__ = [
    # public symbols
    "addUserSpecXmlIfClass",
    "parseAndValidate",
    "parseAndValidateString",
    "parseAndValidateXmlInput",
    "parseAndValidateXmlInputString",
    "parseAndValidateXmlSchema",
    "parseAndValidateXmlSchemaString",
    "XsValidator",
    ]


import string
from minixsv           import *
from xsvalErrorHandler import ErrorHandler
from xsvalBase         import XsValBase
from xsvalSchema       import XsValSchema


_CURRENT_VERSION = "0.5"

_XS_VAL_DEFAULT_ERROR_LIMIT = 20


########################################
# retrieve version of minixsv
#
def getVersion ():
    return _CURRENT_VERSION


########################################
# access function for adding a user specific XML interface class
#
def addUserSpecXmlIfClass (xmlIfKey, factory):
    if not _xmlIfDict.has_key(xmlIfKey):
        _xmlIfDict[xmlIfKey] = factory
    else:
        raise KeyError, "xmlIfKey %s already implemented!" %(xmlIfKey)


########################################
# convenience function for validating
# 1. XML schema file
# 2. XML input file
# If xsdFile is specified, it will be used for validation
# If xsdFile=None, the schemaLocation attribute is expected in the root tag of the XML input file
#
def parseAndValidate (inputFile, xsdFile=None, **kw):
    return parseAndValidateXmlInput (inputFile, xsdFile, 1, **kw)


########################################
# convenience function for validating
# 1. text string containing the XML schema
# 2. text string containing the XML input
# If xsdText is given, it will be used for validation
# If xsdText=None, the schemaLocation attribute is expected in the root tag of the XML input
#
def parseAndValidateString (inputText, xsdText=None, **kw):
    return parseAndValidateXmlInputString (inputText, xsdText, 1, **kw)


########################################
# factory for validating
# 1. XML schema file (only if validateSchema=1)
# 2. XML input file
# If xsdFile is specified, it will be used for validation
# If xsdFile=None, the schemaLocation attribute is expected in the root tag of the XML input file
#
def parseAndValidateXmlInput (inputFile, xsdFile=None, validateSchema=0, **kw):
    xsValidator = XsValidator (**kw)
    # parse XML input file
    inputTreeWrapper = xsValidator.parse (inputFile)
    # validate XML input file
    return xsValidator.validateXmlInput (inputFile, inputTreeWrapper, xsdFile, validateSchema)


########################################
# factory for validating
# 1. text string containing the XML schema (only if validateSchema=1)
# 2. text string containing the XML input
# If xsdText is given, it will be used for validation
# If xsdText=None, the schemaLocation attribute is expected in the root tag of the XML input
#
def parseAndValidateXmlInputString (inputText, xsdText=None, validateSchema=0, **kw):
    xsValidator = XsValidator (**kw)
    # parse XML input text string
    inputTreeWrapper = xsValidator.parseString (inputText)
    # validate XML input text string
    return xsValidator.validateXmlInputString (inputTreeWrapper, xsdText, validateSchema)


########################################
# factory for validating only given XML schema file
#
def parseAndValidateXmlSchema (xsdFile, **kw):
    xsValidator = XsValidator (**kw)
    # parse XML schema file
    xsdTreeWrapper = xsValidator.parse (xsdFile)
    # validate XML schema file
    return xsValidator.validateXmlSchema (xsdFile, xsdTreeWrapper)


########################################
# factory for validating only given XML schema file
#
def parseAndValidateXmlSchemaString (xsdText, **kw):
    xsValidator = XsValidator (**kw)
    # parse XML schema
    xsdTreeWrapper = xsValidator.parseString (xsdText)
    # validate XML schema
    return xsValidator.validateXmlSchema ("", xsdTreeWrapper)


########################################
# XML schema validator class
#
class XsValidator:
    def __init__(self, xmlIfClass=XMLIF_MINIDOM,
                 warningProc=IGNORE_WARNINGS, errorLimit=_XS_VAL_DEFAULT_ERROR_LIMIT, verbose=0):

        self.warningProc   = warningProc
        self.errorLimit    = errorLimit
        self.verbose       = verbose

        # select XML interface class
        self.xmlIf = _xmlIfDict[xmlIfClass](verbose)

        # create error handler
        self.errorHandler  = ErrorHandler (errorLimit, warningProc, verbose)


    ########################################
    # retrieve current version
    #
    def getVersion (self):
        return _CURRENT_VERSION
        

    ########################################
    # parse XML file
    # 'file' may be a filepath or an URI
    #
    def parse (self, file, baseUrl=""):
        self._verbosePrint ("Parsing %s..." %(file))
        return self.xmlIf.parse(file, baseUrl)


    ########################################
    # parse text string containing XML
    #
    def parseString (self, text):
        self._verbosePrint ("Parsing XML text string...")
        return self.xmlIf.parseString(text)


    ########################################
    # validate XML input
    #
    def validateXmlInput (self, xmlInputFile, inputTreeWrapper, xsdFile=None, validateSchema=0):
        # parse XML schema file
        if xsdFile != None:
            xsdTreeWrapper = self.parse (xsdFile)
        else:
            # a schemaLocation attribute is expected in the root tag of the XML input file
            xsdNamespace, xsdFile = self._retrieveReferencedXsdFile (inputTreeWrapper)
            # check namespace
            xsdTreeWrapper = self.parse (xsdFile, inputTreeWrapper.getRootNode().getAbsUrl())

        return self._validateXmlInput (xmlInputFile, xsdFile, inputTreeWrapper, xsdTreeWrapper, validateSchema)


    ########################################
    # validate XML input
    #
    def validateXmlInputString (self, inputTreeWrapper, xsdText=None, validateSchema=0):
        # parse XML schema file
        if xsdText != None:
            xsdFile = "schema text"
            xsdTreeWrapper = self.parseString (xsdText)
        else:
            # a schemaLocation attribute is expected in the root tag of the XML input file
            xsdNamespace, xsdFile = self._retrieveReferencedXsdFile (inputTreeWrapper)
            # check namespace
            xsdTreeWrapper = self.parse (xsdFile, inputTreeWrapper.getRootNode().getAbsUrl())

        return self._validateXmlInput ("input text", xsdFile, inputTreeWrapper, xsdTreeWrapper, validateSchema)


    ########################################
    # validate XML schema separately
    #
    def validateXmlSchema (self, xsdFile, xsdTreeWrapper):
        # parse minixsv internal schema
        rulesTreeWrapper = self.parse(os.path.join (MINIXSV_DIR, "XMLSchema.xsd"))

        self._verbosePrint ("Validating %s..." %(xsdFile))
        xsvGivenXsdFile = XsValSchema (self.xmlIf, self.errorHandler, self.verbose)
        xsvGivenXsdFile.validate(xsdTreeWrapper, rulesTreeWrapper)
        self.errorHandler.flushOutput()
        return xsdTreeWrapper


    ########################################
    # validate XML input tree and xsd tree if requested
    #
    def _validateXmlInput (self, xmlInputFile, xsdFile, inputTreeWrapper, xsdTreeWrapper, validateSchema=0):
        # validate XML schema file if requested
        if validateSchema:
            self.validateXmlSchema (xsdFile, xsdTreeWrapper)

        # check about redefinition of schema location
#        xsdRootNode = xsdTreeWrapper.getRootNode()
#        xsdPrefix = xsdRootNode.getPrefix()
#        childList = xsdRootNode.getXPathList(".//%s:redefine/@schemaLocation" %(xsdPrefix))
#        if childList != []:
#            oldXsdFile = xsdFile
#            xsdFile = childList[0]
#            xsdTreeWrapper = self.parse (xsdFile, baseUrl=oldXsdFile)
#            if validateSchema:
#                self.validateXmlSchema (xsdFile, xsdTreeWrapper)


        self._verbosePrint ("Validating %s..." %(xmlInputFile))
        xsvInputFile = XsValBase (self.xmlIf, self.errorHandler, self.verbose)
        xsvInputFile.validate(inputTreeWrapper, xsdTreeWrapper)
        self.errorHandler.flushOutput()
        return inputTreeWrapper


    ########################################
    # retrieve XML schema location from XML input tree
    #
    def _retrieveReferencedXsdFile (self, inputTreeWrapper):
        # a schemaLocation attribute is expected in the root tag of the XML input file
        for attributeNsLocalName, attributeValue in inputTreeWrapper.getRootNode().getAttributeDict().items():
            if attributeNsLocalName == (XSI_NAMESPACE, "schemaLocation"):
                try:
                    attrValList = string.split(attributeValue)
                    return attrValList[0], attrValList[1]
                except:
                    self.errorHandler.raiseError ("No namespace in 'schemaLocation' attribute specified!")

            elif attributeNsLocalName == (XSI_NAMESPACE, "noNamespaceSchemaLocation"):
                xsdFile = attributeValue
                return None, xsdFile
        else:
            self.errorHandler.raiseError ("No schema file specified!")


    ########################################
    # print if verbose flag is set
    #
    def _verbosePrint (self, text):
        if self.verbose:
            print text


########################################
# factory functions for enabling the selected XML interface class
#
def _interfaceFactoryMinidom (verbose):
    from genxmlif import xmlifMinidom
    return xmlifMinidom.XmlInterfaceMinidom(verbose)

def _interfaceFactory4Dom (verbose):
    from genxmlif import xmlif4Dom
    return xmlif4Dom.XmlInterface4Dom(verbose)

def _interfaceFactoryElementTree (verbose):
    from genxmlif import xmlifElementTree
    return xmlifElementTree.XmlInterfaceElementTree(verbose)


_xmlIfDict = {XMLIF_MINIDOM    :_interfaceFactoryMinidom,
              XMLIF_4DOM       :_interfaceFactory4Dom,
              XMLIF_ELEMENTTREE:_interfaceFactoryElementTree}




