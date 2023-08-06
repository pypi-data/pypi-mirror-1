import re

from txspore import util


class ParsingModel(object):
    """
    The base model object that is used to represent various data once they've
    been parsed from the XML.
    """
    dateAttributes = ["date", "creation", "updated", "created"]
    listAttributes = ["tags"]

    def __init__(self, xmlTree=None):
        if xmlTree is not None:
            self.parseNodes(xmlTree)

    def getNodeTag(self, node):
        return node.tag

    def parseDate(self, date):
        return util.parseXMLDate(date)

    def hasChildren(self, node):
        return bool(node.getchildren())

    def getAttributeNameAndValue(self, node):
        attributeName = self.getNodeTag(node)
        value = node.text or ""
        if attributeName in self.dateAttributes:
            value = self.parseDate(value)
        elif attributeName in self.listAttributes:
            if value == "NULL":
                value = []
            else:
                value = util.stringToList(value)
        elif attributeName == "comments":
            value = []
            for comment in node:
                value.append(Comment(comment))
        elif re.match("^-?\d+$", value):
            value = int(value)
        elif (re.match("^-?\d+\.$", value)
              or re.match("^-?\d+\.\d+$", value)):
            value = float(value)
        elif value == "NULL":
            value = ""
        return (attributeName, value)

    def parseNode(self, node):
        setattr(self, *self.getAttributeNameAndValue(node))

    def parseNodes(self, parentNode):
        for node in parentNode:
            self.parseNode(node)


class CreatureStats(ParsingModel):
    """
    The model object that is used to represent creature stats data once it's
    been parsed from the XML response for a "creature stats" REST request.
    """


class Comment(ParsingModel):
    """
    The model object that is used to represent comment data once it's been
    parsed from the XML response for a "comments for asset" REST request.
    """


class Achievement(ParsingModel):
    """
    The model object that is used to represent achievement data once it's been
    parsed from the XML response for a "achievements for user" REST request.
    """

class DailyStats(ParsingModel):
    """
    The model object that is used to represent daily stats on spore.com once
    they've been parsed from the XML response for a "daily stats" REST request.
    """


class User(ParsingModel):
    """
    The model object that is used to represent a user's profile data once it's
    been parsed from the XML response for a "profile info" REST request.
    """


class SporeCast(ParsingModel):
    """
    The model object that is used to represent spore cast data once it's been
    parsed from the XML response for a "spore casts for user" REST request.
    """


class Asset(ParsingModel):
    """
    The model object that is used to represent spore cast asset data once it's
    been parsed from the XML response for the following REST requests:
        * "assets for user"
        * "assets for spore cast"
        * "asset search"
    """


class AssetInfo(ParsingModel):
    """
    The model object that is used to represent asset data once it's been parsed
    from the XML response for a "info for asset" REST request.
    """


class Buddy(ParsingModel):
    """
    The model object that is used to represent a budy once it's been parsed
    from the XML response for a "buddies for user" REST request.
    """


class RecursiveDataModel(ParsingModel):
    """
    The model object that is used to represent static asset data once it's been
    parsed from the XML response for a "asset data" static data request.
    """

    appendedElements = ["blocks", "childlist", "achievements", "paints",
                        "aestheticTags"]

    def __init__(self, xmlTree=None):
        self._name = self.getNodeTag(xmlTree)
        super(RecursiveDataModel, self).__init__(xmlTree)

    def __repr__(self):
        return "<%sData object>" % self.getName()

    def getName(self):
        return self._name.title()

    def parseNodes(self, parentNode):
        thisClass = self.__class__
        parentTag = self.getNodeTag(parentNode)
        if parentTag in self.appendedElements:
            values = []
            for node in parentNode:
                values.append(thisClass(node))
            setattr(self, parentTag, values)
            return
        for node in parentNode:
            attributeName = self.getNodeTag(node)
            if self.hasChildren(node):
                if attributeName in self.appendedElements:
                    values = []
                    for child in node:
                        if not self.hasChildren(child) and child.text:
                            ignored, value = \
                                self.getAttributeNameAndValue(child)
                            values.append(value)
                        else:
                            values.append(thisClass(child))
                else:
                    values = thisClass(node)
                setattr(self, attributeName, values)
            else:
                self.parseNode(node)


class TagModel(object):

    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return "<%sData object>" % self.getName()

    def getName(self):
        return self._name.title()


class AtomDataModel(RecursiveDataModel):

    atomNameSpace = "http://www.w3.org/2005/Atom"

    def __init__(self, xmlTree=None):
        super(AtomDataModel, self).__init__(xmlTree)
        if self.getName() == "Feed":
            if hasattr(self, "entry"):
                del self.entry
            self.entries = []
            for entry in xmlTree.findall(self.getNSTag("entry")):
                self.entries.append(AtomDataModel(entry))

    def getNSTag(self, tagName):
        return "{%s}%s" % (self.atomNameSpace, tagName)

    def getNodeTag(self, node):
        return util.scrubXMLNameSpace(node.tag)

    def parseDate(self, date):
        return util.parseAtomDate(date)

    def getAttributeNameAndValue(self, node):
        attributeName = self.getNodeTag(node)
        if attributeName == "link":
            value = TagModel("link")
            value.href = node.attrib.get("href")
            value.type = node.attrib.get("type")
            value.length = node.attrib.get("length")
        else:
            attributeName, value = super(
                AtomDataModel, self).getAttributeNameAndValue(node)
        return (attributeName, value)

    def parseNode(self, node):
        if self.getNodeTag(node) == "img":
            obj = TagModel("img")
            for key, value in node.attrib.items():
                setattr(obj, key, value)
            setattr(self, "img", obj)
        else:
            super(AtomDataModel, self).parseNode(node)

    def parseNodes(self, parentNode):
        super(AtomDataModel, self).parseNodes(parentNode)
        for key, value in parentNode.attrib.items():
            setattr(self, key, value)
            #import pdb;pdb.set_trace()

