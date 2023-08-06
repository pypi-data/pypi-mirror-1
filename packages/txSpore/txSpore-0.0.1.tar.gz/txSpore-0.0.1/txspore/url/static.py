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
    return serverString + "/data/achievements.xml"


def achievementIconURL(achievementID):
    raise NotImplementedError


def partInfoURL(blockType):
    return serverString + "/data/blocks/" + blockType + ".xml"

blockMapURL = partInfoURL


def partIconURL(filename):
    unneeded = ["-symmetric", "-center"]
    for unneededFilePart in unneeded:
        if filename.endswith(unneededFilePart):
            filename = filename.replace(unneededFilePart, "")
            continue
    return serverString + "/data/blocks/thumbs/" + filename + ".png"


def paintInfoURL():
    return serverString + "/data/paints/paintmap.xml"

paintMapURL = paintInfoURL


def paintIconURL(filename):
    return serverString + "/data/paints/thumbs/" + filename.lower() + ".png"
