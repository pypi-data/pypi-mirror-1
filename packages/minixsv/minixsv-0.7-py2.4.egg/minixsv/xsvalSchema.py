#
# minixsv, Release 0.7
# file: xsvalSchema.py
#
# Derived validator class (for validation of schema files)
#
# history:
# 2004-10-07 rl   created
# 2006-08-18 rl   W3C testsuite passed for supported features
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


import string
from minixsv import *
from xsvalBase import XsValBase

_localFacetDict = {(XSD_NAMESPACE,"list"): ("length", "minLength", "maxLength", "enumeration", "pattern", "whiteSpace"),
                   (XSD_NAMESPACE,"union"): ("enumeration", "pattern", "whiteSpace"),
                   (XSD_NAMESPACE,"anySimpleType"): ("whiteSpace"),}
###########################################################
#  Derived validator class for validating one input schema file against the XML rules file

class XsValSchema (XsValBase):

    ########################################
    # overloaded validate method
    #
    def validate (self, inputTree, xsdTree):
        XsValBase.validate(self, inputTree, xsdTree)

        self._updateLookupTables (self.inputRoot, self.xsdLookupDict)

        self._includeAndImport (self.inputTree, self.inputTree, self.xsdIncludeDict, self.xsdLookupDict)

        if not self.errorHandler.hasErrors():
            self._checkSchemaSecondLevel()


    ########################################
    # additional checks for schema files which are not covered by "xsStructs.xsd"
    #
    def _checkSchemaSecondLevel(self):

        self._checkElementNodesSecondLevel()
        self._checkAnyNodesSecondLevel()
        self._checkGroupNodesSecondLevel()
        self._checkAttrGroupNodesSecondLevel()
        self._checkAttributeNodesSecondLevel()

        if self.errorHandler.hasErrors():
            return

        self._checkComplexTypesSecondLevel()
        self._checkSimpleTypesSecondLevel()

        self._checkParticlesSecondLevel()

        self._checkIdentityConstraintsSecondLevel()
        self._checkKeyRefsSecondLevel()

    ########################################
    # additional checks for element nodes
    #
    def _checkElementNodesSecondLevel(self):
        elementNodes = self.inputRoot.getElementsByTagNameNS (self.inputNsURI, "element")
        for elementNode in elementNodes:
            if not elementNode.hasAttribute("name") and not elementNode.hasAttribute("ref"):
                self._addError ("Element must have 'name' or 'ref' attribute!", elementNode)
                continue

            if elementNode.hasAttribute("ref"):
                for attrName in ("name", "type", "form"):
                    if elementNode.hasAttribute(attrName):
                        self._addError ("Element with 'ref' attribute must not have '%s' attribute!" %(attrName), elementNode)
                        continue

            complexTypeNode = elementNode.getFirstChildNS (self.inputNsURI, "complexType")
            simpleTypeNode = elementNode.getFirstChildNS (self.inputNsURI, "simpleType")
            if elementNode.hasAttribute("ref") and (complexTypeNode != None or simpleTypeNode != None):
                self._addError ("Element with 'ref' attribute must not have type definition!", elementNode)
                continue
            if elementNode.hasAttribute("type") and (complexTypeNode != None or simpleTypeNode != None):
                self._addError ("Element with 'type' attribute must not have type definition!", elementNode)
                continue
            if not elementNode.hasAttribute("type") and complexTypeNode == None and simpleTypeNode == None:
                self._addWarning ("Element has no type attribute and no type definition!", elementNode)

            if elementNode.hasAttribute("ref"):
                self._checkReference (elementNode, self.xsdElementDict)

            if elementNode.hasAttribute("type"):
                self._checkType (elementNode, "type", self.xsdTypeDict)

            self._checkOccurs (elementNode)
            self._checkFixedDefault(elementNode)

    ########################################
    # additional checks for element nodes
    #
    def _checkAnyNodesSecondLevel(self):
        anyNodes = self.inputRoot.getElementsByTagNameNS (self.inputNsURI, "any")
        for anyNode in anyNodes:
            self._checkOccurs (anyNode)


    ########################################
    # additional checks for group nodes
    #
    def _checkGroupNodesSecondLevel(self):
        groupNodes = self.inputRoot.getElementsByTagNameNS (self.inputNsURI, "group")
        for groupNode in groupNodes:
            if groupNode.hasAttribute("ref"):
                self._checkReference (groupNode, self.xsdGroupDict)
                self._checkOccurs (groupNode)
        if self.errorHandler.hasErrors():
            return
        for groupNode in groupNodes:
            if groupNode.hasAttribute("name"):
                self._checkGroupNodeCircularDef(groupNode, {groupNode["name"]:1})
    
    def _checkGroupNodeCircularDef(self, groupNode, groupNameDict):
        childGroupsRefNodes, dummy, dummy = groupNode.getXPathList (".//%sgroup" %(self.inputNsPrefixString))
        for childGroupRefNode in childGroupsRefNodes:
            if childGroupRefNode.hasAttribute("ref"):
                childGroupNode = self.xsdGroupDict[childGroupRefNode.getQNameAttribute("ref")]
                if not groupNameDict.has_key(childGroupNode["name"]):
                    groupNameDict[childGroupNode["name"]] = 1
                    self._checkGroupNodeCircularDef(childGroupNode, groupNameDict)
                else:
                    self._addError ("Circular definition of group '%s'!" %(childGroupNode["name"]), childGroupNode)
                

    ########################################
    # additional checks for attributeGroup nodes
    #
    def _checkAttrGroupNodesSecondLevel(self):
        attributeGroupNodes = self.inputRoot.getElementsByTagNameNS (self.inputNsURI, "attributeGroup")
        for attributeGroupNode in attributeGroupNodes:
            if attributeGroupNode.hasAttribute("ref"):
                self._checkReference (attributeGroupNode, self.xsdAttrGroupDict)


    ########################################
    # additional checks for attribute nodes
    #
    def _checkAttributeNodesSecondLevel(self):
        attributeNodes = self.inputRoot.getElementsByTagNameNS (XSD_NAMESPACE, "attribute")
        for attributeNode in attributeNodes:
            if self.inputRoot.getAttributeOrDefault("targetNamespace", None) == XSI_NAMESPACE:
                self._addError ("Target namespace of an attribute must not match '%s'!" %(XSI_NAMESPACE), attributeNode)
                
            if not attributeNode.hasAttribute("name") and not attributeNode.hasAttribute("ref"):
                self._addError ("Attribute must have 'name' or 'ref' attribute!", attributeNode)
                continue

            if attributeNode["name"] == "xmlns":
                self._addError ("Attribute must not match 'xmlns'!", attributeNode)

            if attributeNode.hasAttribute("ref"):
                if attributeNode.hasAttribute("name"):
                    self._addError ("Attribute may have 'name' OR 'ref' attribute!", attributeNode)
                if attributeNode.hasAttribute("type"):
                    self._addError ("Attribute may have 'type' OR 'ref' attribute!", attributeNode)
                if attributeNode.hasAttribute("form"):
                    self._addError ("Attribute 'form' is not allowed in this context!", attributeNode)

                if attributeNode.getFirstChildNS(XSD_NAMESPACE, "simpleType") != None:
                    self._addError ("Attribute may only have 'ref' attribute OR 'simpleType' child!", attributeNode)
                
                self._checkReference (attributeNode, self.xsdAttributeDict)

            if attributeNode.hasAttribute("type"):
                if attributeNode.getFirstChildNS(XSD_NAMESPACE, "simpleType") != None:
                    self._addError ("Attribute may only have 'type' attribute OR 'simpleType' child!", attributeNode)

                self._checkType (attributeNode, "type", self.xsdTypeDict, (XSD_NAMESPACE, "simpleType"))

            use = attributeNode.getAttribute("use")
            if use in ("required", "prohibited") and attributeNode.hasAttribute("default"):
                self._addError ("Attribute 'default' is not allowed, because 'use' is '%s'!" %(use), attributeNode)
            
            self._checkFixedDefault(attributeNode)


    ########################################
    # additional checks for complex types
    #
    def _checkComplexTypesSecondLevel(self):
        prefix = self.inputNsPrefixString
        contentNodes, dummy, dummy = self.inputRoot.getXPathList (".//%(prefix)scomplexContent/%(prefix)srestriction | .//%(prefix)scomplexContent/%(prefix)sextension" % vars())
        for contentNode in contentNodes:
            self._checkType(contentNode, "base", self.xsdTypeDict)

        contentNodes, dummy, dummy = self.inputRoot.getXPathList (".//%(prefix)ssimpleContent/%(prefix)srestriction | .//%(prefix)ssimpleContent/%(prefix)sextension" % vars())
        for contentNode in contentNodes:
            baseNsName = contentNode.getQNameAttribute("base")
            if baseNsName != (XSD_NAMESPACE, "anyType"):
                self._checkBaseType(contentNode, baseNsName, self.xsdTypeDict)
            else:
                self._addError ("Referred type must not be 'anyType'!", contentNode)

        # check for duplicate attributes
        complexTypeNodes, dummy, dummy = self.inputRoot.getXPathList (".//%(prefix)scomplexType | .//%(prefix)sextension" % vars())
        for complexTypeNode in complexTypeNodes:
            validAttrDict = {}
            self._updateAttributeDict (complexTypeNode, validAttrDict, 1)

        contentNodes, dummy, dummy = self.inputRoot.getXPathList (".//%(prefix)scomplexType/%(prefix)s*" % vars())
        for contentNode in contentNodes:
            self._checkOccurs (contentNode)


    ########################################
    # additional checks for simple types
    #
    def _checkParticlesSecondLevel(self):
        prefix = self.inputNsPrefixString
        # check for duplicate element names
        particleNodes, dummy, dummy = self.inputRoot.getXPathList (".//%(prefix)sall | .//%(prefix)schoice | .//%(prefix)ssequence" % vars())
        for particleNode in particleNodes:
            elementTypeDict = {}
            elementNameDict = {}
            self._checkContainedElements (particleNode, particleNode.getLocalName(), elementNameDict, elementTypeDict)
                

    def _checkContainedElements (self, node, particleType, elementNameDict, elementTypeDict):
        prefix = self.inputNsPrefixString
        for childNode in node.getChildren():
            childParticleType = childNode.getLocalName()
            if childParticleType in ("sequence", "choice", "all"):
                dummy = {}
                self._checkContainedElements (childNode, childParticleType, dummy, elementTypeDict)
            elif childParticleType in ("group"):
                if childNode["ref"] != None:
                    childGroupNode = self.xsdGroupDict[childNode.getQNameAttribute("ref")]
                    for cChildNode in childGroupNode.getChildren():
                        if cChildNode.getLocalName() != "annotation":
                            self._checkContainedElements (cChildNode, particleType, elementNameDict, elementTypeDict)
                else:
                    for cChildNode in childNode.getChildren():
                        if cChildNode.getLocalName() != "annotation":
                            self._checkContainedElements (cChildNode, particleType, elementNameDict, elementTypeDict)
            else:
                if childNode.getLocalName() == "any":
                    elementName = childNode["namespace"]
                else:
                    elementName = childNode.getAttributeOrDefault("name", childNode["ref"])

                if not elementTypeDict.has_key(elementName):
                    elementTypeDict[elementName] = childNode["type"]
                elif childNode["type"] != elementTypeDict[elementName]:
                    self._addError ("Element '%s' has identical name and different types within '%s'!" %(elementName, particleType), childNode)
                if particleType != "sequence":
                    if not elementNameDict.has_key(elementName):
                        elementNameDict[elementName] = 1
                    else:
                        self._addError ("Element '%s' is not unique within '%s'!" %(elementName, particleType), childNode)


    ########################################
    # additional checks for simple types
    #
    def _checkSimpleTypesSecondLevel(self):
        prefix = self.inputNsPrefixString
        restrictionNodeDict = {}
        restrictionNodes, dummy, dummy = self.inputRoot.getXPathList (".//%(prefix)ssimpleType/%(prefix)srestriction" % vars())
        for restrictionNode in restrictionNodes:
            restrictionNodeDict[restrictionNode.getParentNode()] = restrictionNode
            
            if not restrictionNode.hasAttribute("base") and restrictionNode.getFirstChildNS (self.inputNsURI, "simpleType") == None:
                self._addError ("Simple type restriction must have 'base' attribute or 'simpleType' child tag!", restrictionNode)

            if restrictionNode.hasAttribute("base") and restrictionNode.getFirstChildNS (self.inputNsURI, "simpleType") != None:
                self._addError ("Simple type restriction must not have 'base' attribute and 'simpleType' child tag!", restrictionNode)

            if restrictionNode.hasAttribute("base"):
                self._checkType(restrictionNode, "base", self.xsdTypeDict)

            minExcl = restrictionNode.getFirstChildNS(self.inputNsURI, "minExclusive")
            minIncl = restrictionNode.getFirstChildNS(self.inputNsURI, "minInclusive")
            if minExcl != None and minIncl != None:
                self._addError ("Restriction attributes 'minExclusive' and 'minInclusive' cannot be defined together!", restrictionNode)
            maxExcl = restrictionNode.getFirstChildNS(self.inputNsURI, "maxExclusive")
            maxIncl = restrictionNode.getFirstChildNS(self.inputNsURI, "maxInclusive")
            if maxExcl != None and maxIncl != None:
                self._addError ("Restriction attributes 'maxExclusive' and 'maxInclusive' cannot be defined together!", restrictionNode)

        # check facets of associated primitive type
        for restrictionNode in restrictionNodes:
            try:
                if restrictionNode.hasAttribute("base"):
                    facetNsName = self._getFacetType (restrictionNode, self.xsdTypeDict, restrictionNodeDict)
                    if _localFacetDict.has_key(facetNsName):
                        suppFacets = _localFacetDict[facetNsName]
                    else:
                        suppFacets, dummy, dummy = self.xsdTypeDict[facetNsName].getXPathList (".//hfp:hasFacet/@name" % vars())
                    for childNode in restrictionNode.getChildren():
                        if childNode.getLocalName() != "annotation" and childNode.getLocalName() not in suppFacets:
                            self._addError ("Facet %s not allowed for base type %s!" %(childNode.getLocalName(), restrictionNode["base"]), childNode)
                        elif childNode.getLocalName() == "enumeration":
                            self._checkSimpleType (restrictionNode, "base", childNode, "value", childNode["value"], checkAttribute=1)
            except:
                self._addError ("Primitive type for base type not found!", restrictionNode)

        listNodes, dummy, dummy = self.inputRoot.getXPathList (".//%(prefix)slist" % vars())
        for listNode in listNodes:
            if not listNode.hasAttribute("itemType") and listNode.getFirstChildNS (self.inputNsURI, "simpleType") == None:
                self._addError ("List type must have 'itemType' attribute or 'simpleType' child tag!", listNode)
            elif listNode.hasAttribute("itemType") and listNode.getFirstChildNS (self.inputNsURI, "simpleType") != None:
                self._addError ("List type must not have 'itemType' attribute and 'simpleType' child tag!", listNode)
            elif listNode.hasAttribute("itemType"):
                itemType = self._checkType(listNode, "itemType", self.xsdTypeDict)
                if self.xsdTypeDict.has_key(itemType):
                    if self.xsdTypeDict[itemType].getLocalName() != "simpleType":
                        self._addError ("ItemType '%s' must be a simple type!" %(str(itemType)), listNode)
                    elif self.xsdTypeDict[itemType].getFirstChild().getLocalName() == "list":
                        self._addError ("ItemType '%s' must not be a list type!" %(str(itemType)), listNode)

        unionNodes, dummy, dummy = self.inputRoot.getXPathList (".//%(prefix)ssimpleType/%(prefix)sunion" % vars())
        for unionNode in unionNodes:
            if not unionNode.hasAttribute("memberTypes"):
                for childNode in unionNode.getChildren():
                    if childNode.getLocalName() != "annotation":
                        break
                else:
                    self._addError ("Union must not be empty!", unionNode)
            else:
                for memberType in string.split(unionNode["memberTypes"]):
                    memberNsName = unionNode.qName2NsName(memberType, 1)
                    self._checkBaseType(unionNode, memberNsName, self.xsdTypeDict)
                    if self.xsdTypeDict.has_key(memberNsName):
                        if self.xsdTypeDict[memberNsName].getLocalName() != "simpleType":
                            self._addError ("MemberType '%s' must be a simple type!" %(str(memberNsName)), unionNode)


    ########################################
    # additional checks for keyrefs
    #
    def _checkIdentityConstraintsSecondLevel(self):
        identityConstraintNodes, dummy, dummy = self.inputRoot.getXPathList (".//%sunique" %(self.inputNsPrefixString))
        for identityConstraintNode in identityConstraintNodes:
            selectorNode = identityConstraintNode.getFirstChildNS(XSD_NAMESPACE, "selector")
            try:
                identityConstraintNode.getParentNode().getXPathList (selectorNode["xpath"], selectorNode)
            except Exception, errstr:
                self._addError (errstr, selectorNode)

            try:
                fieldNode = identityConstraintNode.getFirstChildNS(XSD_NAMESPACE, "field")
                identityConstraintNode.getParentNode().getXPathList (fieldNode["xpath"], fieldNode)
            except Exception, errstr:
                self._addError (errstr, fieldNode)


    ########################################
    # additional checks for keyrefs
    #
    def _checkKeyRefsSecondLevel(self):
        keyrefNodes, dummy, dummy = self.inputRoot.getXPathList (".//%skeyref" %(self.inputNsPrefixString))
        for keyrefNode in keyrefNodes:
            self._checkKeyRef(keyrefNode, self.xsdIdentityConstrDict)
                

    ########################################
    # helper methods
    #

    def _checkFixedDefault(self, node):
        if node.hasAttribute("default") and node.hasAttribute("fixed"):
            self._addError ("%s may have 'default' OR 'fixed' attribute!" %(node.getLocalName()), node)
        if  node.hasAttribute("default"):
            self._checkSimpleType (node, "type", node, "default", node["default"], checkAttribute=1)
        if  node.hasAttribute("fixed"):
            self._checkSimpleType (node, "type", node, "fixed", node["fixed"], checkAttribute=1)
    
    
    def _checkReference(self, node, dict):
        baseNsName = node.getQNameAttribute("ref")
        if not dict.has_key(baseNsName):
            self._addError ("Reference '%s' not found!" %(str(baseNsName)), node)

    def _checkType(self, node, typeAttrName, dict, typeNsName=None):
        baseNsName = node.getQNameAttribute(typeAttrName)
        return self._checkBaseType(node, baseNsName, dict, typeNsName)
    
    def _checkBaseType(self, node, baseNsName, dict, typeNsName=None):
        if not dict.has_key(baseNsName) and baseNsName != (XSD_NAMESPACE, "anySimpleType"):
            self._addError ("Definition of type '%s' not found!" %(str(baseNsName)), node)
        else:
            if typeNsName != None and dict[baseNsName].getNsName() != typeNsName:
                self._addError ("Referred type '%s' must be a '%s'!" %(str(baseNsName), str(typeNsName)), node)
        return baseNsName

    def _checkKeyRef(self, keyrefNode, dict):
        baseNsName = keyrefNode.getQNameAttribute("refer")
        if not dict.has_key(baseNsName):
            self._addError ("keyref refers unknown key '%s'!" %(str(baseNsName)), keyrefNode)
        else:
            keyNode = dict[baseNsName]["Node"]
            if keyNode.getNsName() not in ((XSD_NAMESPACE, "key"), (XSD_NAMESPACE, "unique")):
                self._addError ("reference to non-key constraint '%s'!" %(str(baseNsName)), keyrefNode)
            if len(keyrefNode.getChildrenNS(XSD_NAMESPACE, "field")) != len(keyNode.getChildrenNS(XSD_NAMESPACE, "field")):
                self._addError ("key/keyref field size mismatch!", keyrefNode)
                
            
    def _checkOccurs (self, node):
        minOccurs = node.getAttributeOrDefault("minOccurs", "1")
        maxOccurs = node.getAttributeOrDefault("maxOccurs", "1")
        if maxOccurs != "unbounded":
            if string.atoi(minOccurs) > string.atoi(maxOccurs):
                self._addError ("Attribute minOccurs > maxOccurs!", node)


    def _getFacetType(self, node, xsdTypeDict, restrictionNodeDict):
        baseNsName = node.getQNameAttribute("base")
        if baseNsName == (XSD_NAMESPACE, "anySimpleType"):
            return (XSD_NAMESPACE, "anySimpleType")
        else:
            baseNode = xsdTypeDict[baseNsName]
            if baseNode["facetType"] != None:
                facetType = baseNode.qName2NsName(baseNode["facetType"], 1)
                node.getParentNode()["facetType"] = node.nsName2QName(facetType)
                return facetType
            else:
                for baseNodeType in ("list", "union"):
                    if baseNode.getFirstChildNS (XSD_NAMESPACE, baseNodeType) != None:
                        return (XSD_NAMESPACE, baseNodeType)
                else:
                    return self._getFacetType(restrictionNodeDict[baseNode], xsdTypeDict, restrictionNodeDict)    


