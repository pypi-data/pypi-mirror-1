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

    def hasChildren(self, node):
        return bool(node.getchildren())

    def getAttributeNameAndValue(self, node):
        attributeName = node.tag
        value = node.text or ""
        if attributeName in self.dateAttributes:
            value = util.parseXMLDate(value)
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
        return attributeName, value

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
        self._name = xmlTree.tag
        super(RecursiveDataModel, self).__init__(xmlTree)

    def __repr__(self):
        return "<%sData object>" % self.getName()

    def getName(self):
        return self._name.title()

    def parseNodes(self, parentNode):
        if parentNode.tag in self.appendedElements:
            values = []
            for node in parentNode:
                values.append(RecursiveDataModel(node))
            setattr(self, parentNode.tag, values)
            return
        for node in parentNode:
            attributeName = node.tag
            if self.hasChildren(node):
                if attributeName in self.appendedElements:
                    values = []
                    for child in node:
                        if not self.hasChildren(child) and child.text:
                            ignored, value = \
                                self.getAttributeNameAndValue(child)
                            values.append(value)
                        else:
                            values.append(RecursiveDataModel(child))
                else:
                    values = RecursiveDataModel(node)
                setattr(self, attributeName, values)
            else:
                self.parseNode(node)
