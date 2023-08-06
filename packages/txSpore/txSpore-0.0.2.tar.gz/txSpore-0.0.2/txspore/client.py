from twisted.internet.defer import succeed
from twisted.internet.threads import deferToThread
from twisted.python import log
from twisted.python.filepath import FilePath
from twisted.web.client import getPage

from txspore import model
from txspore import util
from txspore.url import atom, data, rest, currentSaveDir


class Cache(object):
    """
    A caching object. This is indended to be used by client implementations.
    """
    def __init__(self):
        self._cache = {}

    def set(self, key, object):
        self._cache[key] = object

    def get(self, key):
        return self._cache.get(key)

    def remove(self, key):
        del self._cache[key]

    def purge(self):
        self._cache = {}


class Aspect(object):
    """
    The base class for secondary objects ("aspects", to abuse a term) that
    encapsulate specific functionality for spore service and data clients.
    """
    def __init__(self, parent=None):
        self.parent = parent


class RESTAspect(Aspect):
    """
    This class encapsulates the REST functionality published on spore.com. It
    is intended to be instantiated as an attribute on spore clients.
    """
    def _getXMLForREST(self, url):
        d = self.parent.openURL(url)
        d.addCallback(util.XML)
        d.addErrback(util.logError)
        return d

    def _getModelsForSubNodes(self, tree, tagName, modelClass):
        """
        This function is intended to be used as a callback by the REST client
        functions.

        @param tree: the element tree the be searched
        @param tagName: the tag name to search; should be a child node in the
            passed tree
        @param modelClass: the class from the txspore.model module that should
            be instantiated with each found child node.
        """
        models = []
        for assetNode in tree.findall(tagName):
            models.append(modelClass(assetNode))
        return models

    def getDailyStats(self):
        url = rest.dailyStatsURL()
        d = self._getXMLForREST(url)
        d.addCallback(model.DailyStats)
        return d

    def getStatsForCreature(self, creatureID):
        url = rest.creatureStatsURL(creatureID)
        d = self._getXMLForREST(url)
        d.addCallback(model.CreatureStats)
        return d

    def getProfileInfo(self, username):
        url = rest.profileInfoURL(username)
        d = self._getXMLForREST(url)
        d.addCallback(model.User)
        return d

    def getAssetsForUser(self, username, start, length):
        """
        @param username: the username for the assets' creator
        @param start: the start index of the user's assets
        @param length: the number of assets to return
        """
        url = rest.assetsForUserURL(username, start, length)
        d = self._getXMLForREST(url)
        d.addCallback(self._getModelsForSubNodes, "asset", model.Asset)
        return d

    def getSporeCastsForUser(self, username):
        url = rest.sporeCastsForUserURL(username)
        d = self._getXMLForREST(url)
        d.addCallback(self._getModelsForSubNodes, "sporecast", model.SporeCast)
        return d

    def getAssetsForSporeCast(self, sporeCastID, start, length):
        """
        @param sporeCastID: the ID for the spore cast
        @param start: the start index of the user's assets
        @param length: the number of assets to return
        """
        url = rest.assetsForSporeCastURL(sporeCastID, start, length)
        d = self._getXMLForREST(url)
        d.addCallback(self._getModelsForSubNodes, "asset", model.Asset)
        return d

    # XXX This function currently returns a list of useless model objects...
    # the achievement model needs more than just a meaningless guid and
    # datetime stamp.  The name of the achievement as well as icon/image urls
    # should be included.  This will mean performing additional searches.
    def getAchievementsForUser(self, username, start, length):
        """
        @param username: the username for the achiever
        @param start: the start index of the user's achievements
        @param length: the number of achievements to return
        """
        url = rest.achievementsForUserURL(username, start, length)
        d = self._getXMLForREST(url)
        d.addCallback(
            self._getModelsForSubNodes, "achievement", model.Achievement)
        return d

    def getInfoForAsset(self, assetID):

        url = rest.infoForAssetURL(assetID)
        d = self._getXMLForREST(url)
        d.addCallback(model.AssetInfo)
        return d

    def getCommentsForAsset(self, assetID, start, length):
        """
        @param assetID: the ID for the desired asset
        @param start: the start index of the asset's comments
        @param length: the number of comments to return
        """
        url = rest.commentsForAssetURL(assetID, start, length)
        d = self._getXMLForREST(url)
        d.addCallback(self._getModelsForSubNodes, "comment", model.Comment)
        return d

    def getBuddiesForUser(self, username, start, length):
        """
        @param username: the username for the person with the buddies
        @param start: the start index of the user's buddies
        @param length: the number of buddies to return
        """
        url = rest.buddiesForUserURL(username, start, length)
        d = self._getXMLForREST(url)
        d.addCallback(self._getModelsForSubNodes, "buddy", model.Buddy)
        return d

    def searchAssets(self, searchType, start, length, assetType=""):
        """
        @param searchType: the kind of search to perform; legal values for this
            parameter are:
                TOP_RATED, TOP_RATED_NEW, NEWEST, FEATURED,
                MAXIS_MADE, RANDOM, CUTE_AND_CREEPY.
        @param start: the start index of the user's buddies
        @param length: the number of buddies to return
        @param assetType: optional asset type to search for; legal values for
            this parameter are:
                UFO, CREATURE, BUILDING, VEHICLE.
        """
        searchType = util.validateParameters(searchType, [
            "TOP_RATED", "TOP_RATED_NEW", "NEWEST", "FEATURED", "MAXIS_MADE",
            "RANDOM", "CUTE_AND_CREEPY"])
        assetType = util.validateParameters(assetType, [
            "UFO", "CREATURE", "BUILDING", "VEHICLE"])
        url = rest.assetSearchURL(searchType, start, length, assetType)
        d = self._getXMLForREST(url)
        d.addCallback(self._getModelsForSubNodes, "asset", model.Asset)
        return d


class StaticDataAspect(Aspect):
    """
    This class encapsulates the functionality for obtaining the static data
    resources published on spore.com. It is intended to be instantiated as an
    attribute on spore clients.
    """

    def _blockingSave(self, data, path, filename):
        """
        A function that saves a file to a given directory, creating the
        directories above the destination, if needed.

        This function is intended to be called from a thread.
        """
        path = FilePath(path)
        if not path.exists():
            path.makedirs()
        file = path.child(filename)
        file.setContent(data)
        return file.path

    def _saveFile(self, data, path, filename):
        """
        This file-saving function runs all the code (that would normally block
        an application) in a thread, deferring the result by running it in a
        thread.
        """
        d = deferToThread(self._blockingSave, data, path, filename)
        d.addErrback(util.logError)
        return d

    def _saveToFileDescriptor(self, data, fd):
        """
        Write data to an open file descriptor.

        This function is intended to be called from a thread.
        """
        d = deferToThread(fd.write, data)
        d.addErrback(util.logError)
        return d

    def _fetchAndSave(self, url, filename=None, path=None, fd=None,
                     skipCache=False):
        d = self.parent.openURL(url)
        if fd:
            log.msg("Preparing to save in an open file descriptor ...")
            d.addCallback(self._saveToFileDescriptor, fd)
            return d
        elif path:
            log.msg("Preparing to save in custom directory, %s ..." % path)
        else:
            path = currentSaveDir
            log.msg("Preparing to save in default directory, %s ..." % path)
        d.addCallback(self._saveFile, path, filename)
        return d

    def getLargeCard(self, assetID, path=None, fd=None):
        return self._fetchAndSave(
            data.largeCardURL(assetID), assetID + "_lrg_card.png", path, fd)

    def getAssetDataXML(self, assetID, path=None, fd=None):
        return self._fetchAndSave(
            data.assetDataXMLURL(assetID),
            assetID + ".xml", path, fd)

    def getAssetDataLargePNG(self, assetID, path=None, fd=None):
        return self._fetchAndSave(
            data.assetDataLargePNGURL(assetID),
            assetID + "_lrg.png", path, fd)

    def getAssetDataSmallPNG(self, assetID, path=None, fd=None):
        return self._fetchAndSave(
            data.assetDataSmallPNGURL(assetID),
            assetID + ".png", path, fd)

    def getAchievementIcon(self, achievementID, path=None, fd=None):
        return self._fetchAndSave(
            data.achievementIconURL(achievementID),
            achievementID + ".png", path, fd)

    def getAchievementDataXML(self, path=None, fd=None):
        return self._fetchAndSave(
            data.achievementDataXMLURL(), "achievements.xml", path, fd)

    getAchievementText = getAchievementDataXML

    def getPartInfo(self, blockType="", path=None, fd=None):
        """
        @param blockType: has the following valid values:
                creature, limb, building, vehicle
            If the value is left empty, all block types will be returned.
        """
        blockType = util.validateParameters(blockType, [
            "creature", "limb", "building", "vehicle", ""])
        blockFilename = blockType + "blockmap"
        return self._fetchAndSave(
            data.partInfoURL(blockFilename),
            blockFilename + ".xml", path, fd)

    def getPartIcon(self, remoteFilename, path=None, fd=None):
        return self._fetchAndSave(
            data.partIconURL(remoteFilename),
            remoteFilename + ".png", path, fd)

    def getPaintInfo(self, path=None, fd=None):
        """
        The objects returned from this call will have the following attributes:
            * id
            * filename
        In addition, they may also have this attribute:
            * aestheticTags (list-type)
        """
        return self._fetchAndSave(
            data.paintInfoURL(), "paintmap.xml",  path, fd)

    def getPaintIcon(self, remoteFilename, path=None, fd=None):
        return self._fetchAndSave(
            data.paintIconURL(remoteFilename),
            remoteFilename + ".png", path, fd)


class AtomAspect(Aspect):

    def _getXMLForAtom(self, url):
        d = self.parent.openURL(url)
        d.addCallback(util.XML)
        d.addErrback(util.logError)
        return d

    def getAssetsForUser(self, username):
        """
        @param username: the username for the assets' creator
        @param start: the start index of the user's assets
        @param length: the number of assets to return
        """
        url = atom.assetsForUserURL(username)
        d = self._getXMLForAtom(url)
        d.addCallback(model.AtomDataModel)
        d.addErrback(util.logError)
        return d

    def getEventsForUser(self, username):
        url = atom.eventsForUserURL(username)
        d = self._getXMLForAtom(url)
        d.addCallback(model.AtomDataModel)
        d.addErrback(util.logError)
        return d

    def getEventsForAsset(self, assetID):
        url = atom.eventsForAssetURL(assetID)
        d = self._getXMLForAtom(url)
        d.addCallback(model.AtomDataModel)
        d.addErrback(util.logError)
        return d

    def getSporeCastFeed(self, sporeCastID):
        url = atom.sporeCastFeedURL(sporeCastID)
        d = self._getXMLForAtom(url)
        d.addCallback(model.AtomDataModel)
        d.addErrback(util.logError)
        return d

    def searchAssets(self, searchType, start, length):
        """
        @param searchType: the kind of search to perform; legal values for this
            parameter are:
                TOP_RATED, TOP_RATED_NEW, NEWEST, FEATURED, MAXIS_MADE, RANDOM,
                CUTE_AND_CREEPY
        @param start: the start index of the user's buddies
        @param length: the number of buddies to return
        """
        url = atom.assetSearchURL(searchType, start, length)
        d = self._getXMLForAtom(url)
        d.addCallback(model.AtomDataModel)
        d.addErrback(util.logError)
        return d


class CustomAspect(Aspect):
    """
    This class offers an API with methods considered convenient or that have
    been requested by memebers of the community. These methods often use
    methods from the classes that reflect the official Spore API, combining
    them to provide other useful data correltations.
    """


class AsyncClient(object):
    """
    A caching-capable, async client for services and data published on
    spore.com.

    Currently, if you want to override the cache for a function call, you need
    to delete the entry in the cache. There are two options available for this:
    just the key (url) that you want to re-fetch, or you can purge the whole
    cache:

        >>> myclient.cache.remove("http://some.url/")
    or
        >>> myclient.cache.purge()

    Eventually, each API method will support a "skipCache" keyoword parameter.
    """
    def __init__(self):
        self.rest = RESTAspect(parent=self)
        self.data = StaticDataAspect(parent=self)
        self.atom = AtomAspect(parent=self)
        self.cache = Cache()

    def _setCache(self, data, url):
        self.cache.set(url, data)
        return data

    def openURL(self, url, skipCache=False):
        """
        @param url: the URL to get
        @param skipCache: a boolean value; if True, the cache will not be used
        """
        cachedData = self.cache.get(url)
        if cachedData is None or skipCache:
            d = getPage(url)
            d.addErrback(util.logError)
            d.addCallback(self._setCache, url)
        else:
            d = succeed(cachedData)
        return d
