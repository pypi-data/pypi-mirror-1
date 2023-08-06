from twisted.internet.threads import deferToThread
from twisted.python import log
from twisted.python.filepath import FilePath
from twisted.web.client import getPage

from txspore import model
from txspore.url import rest, static, currentSaveDir
from txspore.util import logError, XML


def openURL(url):
    d = getPage(url)
    d.addErrback(logError)
    return d


# The following functions correspond to the REST API provided by spore.com.


def getXMLForREST(url):
    d = openURL(url)
    d.addCallback(XML)
    d.addErrback(logError)
    return d


# XXX there is no unit test for this yet
def getModelsForSubNodes(tree, tagName, modelClass):
    """
    This function is intended to be used as a callback by the REST client
    functions.

    @param tree: the element tree the be searched
    @param tagName: the tag name to search; should be a child node in the
        passed tree
    @param modelClass: the class from the txspore.model module that should be
        instantiated with each found child node.
    """
    models = []
    for assetNode in tree.findall(tagName):
        models.append(modelClass(assetNode))
    return models


def getDailyStats():
    url = rest.dailyStatsURL()
    d = getXMLForREST(url)
    d.addCallback(model.DailyStats)
    return d


def getStatsForCreature(creatureID):
    url = rest.creatureStatsURL(creatureID)
    d = getXMLForREST(url)
    d.addCallback(model.CreatureStats)
    return d


def getProfileInfo(username):
    url = rest.profileInfoURL(username)
    d = getXMLForREST(url)
    d.addCallback(model.User)
    return d


def getAssetsForUser(username, start, length):
    """
    @param username: the username for the assets' creator
    @param start: the start index of the user's assets
    @param length: the number of assets to return
    """
    url = rest.assetsForUserURL(username, start, length)
    d = getXMLForREST(url)
    d.addCallback(getModelsForSubNodes, "asset", model.Asset)
    return d


def getSporeCastsForUser(username):

    url = rest.sporeCastsForUserURL(username)
    d = getXMLForREST(url)
    d.addCallback(getModelsForSubNodes, "sporecast", model.SporeCast)
    return d


def getAssetsForSporeCast(sporeCastID, start, length):
    """
    @param sporeCastID: the ID for the spore cast
    @param start: the start index of the user's assets
    @param length: the number of assets to return
    """
    url = rest.assetsForSporeCastURL(sporeCastID, start, length)
    d = getXMLForREST(url)
    d.addCallback(getModelsForSubNodes, "asset", model.Asset)
    return d


# XXX This function currently returns a list of useless model objects... the
# achievement model needs more than just a meaningless guid and datetime stamp.
# The name of the achievement as well as icon/image urls should be included.
# This will mean performing additional searches.
def getAchievementsForUser(username, start, length):
    """
    @param username: the username for the achiever
    @param start: the start index of the user's achievements
    @param length: the number of achievements to return
    """
    url = rest.achievementsForUserURL(username, start, length)
    d = getXMLForREST(url)
    d.addCallback(getModelsForSubNodes, "achievement", model.Achievement)
    return d


def getInfoForAsset(assetID):

    url = rest.infoForAssetURL(assetID)
    d = getXMLForREST(url)
    d.addCallback(model.AssetInfo)
    return d


def getCommentsForAsset(assetID, start, length):
    """
    @param assetID: the ID for the desired asset
    @param start: the start index of the asset's comments
    @param length: the number of comments to return
    """
    url = rest.commentsForAssetURL(assetID, start, length)
    d = getXMLForREST(url)
    d.addCallback(getModelsForSubNodes, "comment", model.Comment)
    return d


def getBuddiesForUser(username, start, length):
    """
    @param username: the username for the person with the buddies
    @param start: the start index of the user's buddies
    @param length: the number of buddies to return
    """
    url = rest.buddiesForUserURL(username, start, length)
    d = getXMLForREST(url)
    d.addCallback(getModelsForSubNodes, "buddy", model.Buddy)
    return d


def searchAssets(searchType, start, length, assetType=""):
    """
    @param searchType: the kind of search to perform; legal values for this
        parameter are: TOP_RATED, TOP_RATED_NEW, NEWEST, FEATURED, MAXIS_MADE,
        RANDOM, CUTE_AND_CREEPY.
    @param start: the start index of the user's buddies
    @param length: the number of buddies to return
    @param assetType: optional asset type to search for; legal values for this
        parameter are: UFO, CREATURE, BUILDING, VEHICLE.
    """
    # XXX add a validation check for legal parameters
    url = rest.assetSearchURL(searchType, start, length, assetType)
    d = getXMLForREST(url)
    d.addCallback(getModelsForSubNodes, "asset", model.Asset)
    return d


# The following functions correspond to the "static data" API provided by
# spore.com.


def blockingSave(data, path, filename):
    """
    A function that saves a file to a given directory, creating the directories
    above the destination, if needed.

    This function is intended to be called from a thread.
    """
    path = FilePath(path)
    if not path.exists():
        path.makedirs()
    file = path.child(filename)
    file.setContent(data)
    return file.path


def saveFile(data, path, filename):
    """
    This file-saving function runs all the code (that would normally block an
    application) in a thread, deferring the result by running it in a thread.
    """
    d = deferToThread(blockingSave, data, path, filename)
    d.addErrback(logError)
    return d


def saveToFileDescriptor(data, fd):
    """
    Write data to an open file descriptor.

    This function is intended to be called from a thread.
    """
    d = deferToThread(fd.write, data)
    d.addErrback(logError)
    return d


def fetchAndSave(url, filename=None, path=None, fd=None):
    d = openURL(url)
    if fd:
        log.msg("Preparing to save in an open file descriptor ...")
        d.addCallback(saveToFileDescriptor, fd)
        return d
    elif path:
        log.msg("Preparing to save in custom directory, %s ..." % path)
    else:
        path = currentSaveDir
        log.msg("Preparing to save in default directory, %s ..." % path)
    d.addCallback(saveFile, path, filename)
    return d


def getLargeCard(assetID, path=None, fd=None):
    return fetchAndSave(
        static.largeCardURL(assetID), assetID + "_lrg_card.png", path, fd)


def getAssetDataXML(assetID, path=None, fd=None):
    return fetchAndSave(
        static.assetDataXMLURL(assetID),
        assetID + ".xml", path, fd)


def getAssetDataLargePNG(assetID, path=None, fd=None):
    return fetchAndSave(
        static.assetDataLargePNGURL(assetID),
        assetID + "_lrg.png", path, fd)


def getAssetDataSmallPNG(assetID, path=None, fd=None):
    return fetchAndSave(
        static.assetDataSmallPNGURL(assetID),
        assetID + ".png", path, fd)


def getAchievementIcon(achievementID, path=None, fd=None):
    raise NotImplementedError


def getAchievementDataXML(path=None, fd=None):
    return fetchAndSave(
        static.achievementDataXMLURL(), "achievements.xml", path, fd)

getAchievementText = getAchievementDataXML


def getPartInfo(blockType="", path=None, fd=None):
    """
    @param blockType: has the following valid values:
            creature, limb, building, vehicle
        If the value is left empty, all block types will be returned.
    """
    # XXX add a validation check for legal parameters
    blockFilename = blockType + "blockmap"
    return fetchAndSave(
        static.partInfoURL(blockFilename), blockFilename + ".xml", path, fd)


def getPartIcon(remoteFilename, path=None, fd=None):
    return fetchAndSave(
        static.partIconURL(remoteFilename), remoteFilename + ".png", path, fd)


def getPaintInfo(path=None, fd=None):
    """
    The objects returned from this call will have the following attributes:
        * id
        * filename
    In addition, they may also have this attribute:
        * aestheticTags (list-type)
    """
    return fetchAndSave(
        static.paintInfoURL(), "paintmap.xml",  path, fd)


def getPaintIcon(remoteFilename, path=None, fd=None):
    return fetchAndSave(
        static.paintIconURL(remoteFilename), remoteFilename + ".png", path, fd)
