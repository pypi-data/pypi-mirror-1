"""
The original API seems to be unmaintained. As such, we import what we can use,
and reimplement the rest.
"""
from txspore.original.SporeAPICoreUtils import (
    LargeCard as largeCardURL,
    XMLURL as assetDataXMLURL,
    LargeAssetURL as assetDataLargePNGURL,
    AssetURL as assetDataSmallPNGURL,
    )
from txspore.url import serverString


def achievementDataXMLURL():
    return "%s/data/achievements.xml" % serverString


def achievementIconURL(achievementID):
    return "%s/static/war/images/achievements/%s.png" % (
        serverString, achievementID)


def partInfoURL(blockType):
    return "%s/data/blocks/%s.xml" % (serverString, blockType)

blockMapURL = partInfoURL


def partIconURL(filename):
    unneeded = ["-symmetric", "-center"]
    for unneededFilePart in unneeded:
        if filename.endswith(unneededFilePart):
            filename = filename.replace(unneededFilePart, "")
            continue
    return "%s/data/blocks/thumbs/%s.png" % (serverString, filename)


def paintInfoURL():
    return "%s/data/paints/paintmap.xml" % serverString

paintMapURL = paintInfoURL


def paintIconURL(filename):
    return "%s/data/paints/thumbs/%s.png" % (serverString, filename.lower())
