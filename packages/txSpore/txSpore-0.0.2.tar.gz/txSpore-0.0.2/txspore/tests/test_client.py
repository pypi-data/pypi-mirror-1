from cStringIO import StringIO
from datetime import datetime
from functools import partial

from twisted.internet import reactor
from twisted.internet.defer import succeed, fail
from twisted.internet.threads import deferToThreadPool
from twisted.python.filepath import FilePath
from twisted.python.threadpool import ThreadPool

from txspore import client
from txspore import model
from txspore import util
from txspore.client import AsyncClient
from txspore.testing import payload
from txspore.testing.base import TXSporeTestCase


class CacheTestCase(TXSporeTestCase):

    def test_creation(self):
        cache = client.Cache()
        self.assertEquals(cache._cache, {})

    def test_set(self):
        cache = client.Cache()
        cache.set("mykey", "myvalue")
        self.assertEquals(cache._cache["mykey"], "myvalue")

    def test_get(self):
        cache = client.Cache()
        self.assertEquals(cache.get("mykey"), None)
        cache.set("mykey", "myvalue")
        self.assertEquals(cache.get("mykey"), "myvalue")

    def test_remove(self):
        cache = client.Cache()
        cache.set("mykey1", "myvalue1")
        cache.set("mykey2", "myvalue2")
        self.assertEquals(cache.get("mykey1"), "myvalue1")
        self.assertEquals(cache.get("mykey2"), "myvalue2")
        cache.remove("mykey1")
        self.assertEquals(cache.get("mykey1"), None)
        self.assertEquals(cache.get("mykey2"), "myvalue2")

    def test_purge(self):
        cache = client.Cache()
        cache.set("mykey1", "myvalue1")
        cache.set("mykey2", "myvalue2")
        self.assertEquals(cache.get("mykey1"), "myvalue1")
        self.assertEquals(cache.get("mykey2"), "myvalue2")
        cache.purge()
        self.assertEquals(cache.get("mykey1"), None)
        self.assertEquals(cache.get("mykey2"), None)


class AspectTestCase(TXSporeTestCase):

    def test_creation(self):
        someClient = object()
        aspect = client.Aspect(parent=someClient)
        self.assertEquals(aspect.parent, someClient)


class RESTAspectTestCase(TXSporeTestCase):

    def setUp(self):
        super(RESTAspectTestCase, self).setUp()
        self.client = client.AsyncClient()
        self.restAspect = self.client.rest

    def test_getXMLForREST(self):

        def checkForXML(result):
            children = [x.tag for x in result]
            expected = ['totalUploads', 'dayUploads', 'totalUsers', 'dayUsers']
            self.assertEquals(children, expected)
            self.assertEquals(result.tag, "stats")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTDailyStatsResponse)

        d = self.restAspect._getXMLForREST("http://some.spore.url")
        d.addCallback(checkForXML)
        return d

    def test_getXMLForRestWithError(self):
        self.addCleanup(setattr, self.client, "openURL", self.client.openURL)
        self.client.openURL = lambda url: fail(RuntimeError("oops"))

        d = self.restAspect._getXMLForREST("http://some.spore.url")
        self.assertFailure(d, RuntimeError)
        logged = self.catcher.pop()
        self.assertEquals(logged["message"][0], "ERROR: oops")

    def test_getModelsForSubNodes(self):
        xmlBytes = "<xml><top><child>A</child></top></xml>"
        xmlTree = util.XML(xmlBytes)
        models = self.restAspect._getModelsForSubNodes(
            xmlTree, "top", model.ParsingModel)
        self.assertEquals(len(models), 1)
        self.assertEquals(models[0].child, "A")

    def test_getDailyStats(self):

        def checkModel(model):
            self.assertEquals(model.totalUploads, 121325142)
            self.assertEquals(model.dayUploads, 88683)
            self.assertEquals(model.totalUsers, 3055769)
            self.assertEquals(model.dayUsers, 1235)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTDailyStatsResponse)

        d = self.restAspect.getDailyStats()
        d.addCallback(checkModel)
        return d

    def test_getStatsForCreature(self):

        def checkModel(model):
            self.assertEquals(model.status, 1)
            self.assertEquals(model.input, 500327625969)
            self.assertEquals(model.cost, 1925)
            self.assertEquals(model.health, 5.0)
            self.assertEquals(model.height, 0.99036040)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTCreatureStatsResponse)

        d = self.restAspect.getStatsForCreature("500327625969")
        d.addCallback(checkModel)
        return d

    def test_getProfileInfo(self):

        def checkModel(model):
            self.assertEquals(model.status, 1)
            self.assertEquals(model.input, "oubiwann")
            self.assertEquals(model.id, 2263046854)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTProfileInfoResponse)

        d = self.restAspect.getProfileInfo("oubiwann")
        d.addCallback(checkModel)
        return d

    def test_getAssetsForUser(self):

        def checkModel(assets):
            self.assertEquals(len(assets), 4)
            self.assertEquals(assets[0].id, 500447356422)
            self.assertEquals(assets[0].name, "Borziadinid")
            self.assertEquals(assets[0].type, "CREATURE")
            self.assertEquals(assets[1].id, 500438943083)
            self.assertEquals(assets[1].name, "Borziadinid")
            self.assertEquals(assets[2].name, "Eicorn")
            self.assertEquals(assets[3].name, "Swamp Skipper")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTAssetsForUserResponse)

        d = self.restAspect.getAssetsForUser("oubiwann", 0, 4)
        d.addCallback(checkModel)
        return d

    def test_getSporeCastsForUser(self):

        def checkModel(casts):
            self.assertEquals(len(casts), 2)
            self.assertEquals(casts[0].id, 500384059016)
            self.assertEquals(casts[0].title, "Clark and Stanley")
            self.assertEquals(casts[1].id, 500271573592)
            self.assertEquals(casts[1].title, "Cool Structures")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTSporeCastsForUserResponse)

        d = self.restAspect.getSporeCastsForUser("oubiwann")
        d.addCallback(checkModel)
        return d

    def test_getAssetsForSporeCast(self):

        def checkModel(assets):
            self.assertEquals(len(assets), 3)
            self.assertEquals(assets[0].id, 500378366841)
            self.assertEquals(assets[0].name, "Mountain Nurble")
            self.assertEquals(assets[1].id, 500372073131)
            self.assertEquals(assets[1].name, "Pumpkipod")
            self.assertEquals(assets[2].id, 500284482417)
            self.assertEquals(assets[2].name, "Ponlarin")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTAssetsForSporeCastResponse)

        d = self.restAspect.getAssetsForSporeCast("oubiwann", 0, 3)
        d.addCallback(checkModel)
        return d

    def test_getAchievementsForUser(self):

        def checkModel(achievements):
            self.assertEquals(len(achievements), 2)
            self.assertEquals(achievements[0].guid, "0xaec66642!0x0770b845")
            self.assertEquals(
                achievements[0].date, datetime(2009, 8, 9, 18, 10, 35))
            self.assertEquals(achievements[1].guid, "0x0cc8b2c9!0xb9ff8f07")
            self.assertEquals(
                achievements[1].date, datetime(2009, 7, 8, 5, 45, 3))

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTAchievementsForUserResponse)

        d = self.restAspect.getAchievementsForUser("oubiwann", 0, 2)
        d.addCallback(checkModel)
        return d

    def test_getInfoForAsset(self):

        def checkModel(model):
            self.assertEquals(model.status, 1)
            self.assertEquals(model.input, 500327625969)
            self.assertEquals(model.name, "Durnipin")
            self.assertEquals(model.author, "oubiwann")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTInfoForAssetResponse)

        d = self.restAspect.getInfoForAsset("500327625969")
        d.addCallback(checkModel)
        return d

    def test_getCommentsForAsset(self):

        def checkModel(comments):
            self.assertEquals(len(comments), 2)
            self.assertEquals(
                comments[0].message,
                ("This is a second comment for testing the API (Twisted "
                 "Python async Spore API)."))
            self.assertEquals(comments[0].sender, "oubiwann")
            self.assertEquals(
                comments[1].message,
                "This comment is used for testing the API")
            self.assertEquals(comments[1].sender, "oubiwann")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTCommentsForAssetResponse)

        d = self.restAspect.getCommentsForAsset("500327625969", 0, 2)
        d.addCallback(checkModel)
        return d

    def test_getBuddiesForUser(self):

        def checkModel(buddies):
            self.assertEquals(len(buddies), 2)
            self.assertEquals(buddies[0].id, 2260775701)
            self.assertEquals(buddies[0].name, "Azulon")
            self.assertEquals(buddies[1].id, 2263135745)
            self.assertEquals(buddies[1].name, "Emmande")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTBuddiesForUserResponse)

        d = self.restAspect.getBuddiesForUser("oubiwann", 0, 2)
        d.addCallback(checkModel)
        return d

    def test_searchAssets(self):

        def checkModel(assets):
            self.assertEquals(len(assets), 4)
            self.assertEquals(assets[0].id, 500447216760)
            self.assertEquals(assets[0].name, "Goring")
            self.assertEquals(assets[1].name, "Kang")
            self.assertEquals(assets[2].name, "Grumsley2")
            self.assertEquals(assets[3].name, "Juko")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleRESTAssetSearchResponse)

        d = self.restAspect.searchAssets("MAXIS_MADE", 0, 4, "CREATURE")
        d.addCallback(checkModel)
        return d

    def test_searchAssetsInvalidSearchType(self):

        self.assertRaises(ValueError, self.restAspect.searchAssets, 
                          "WRONG_VALUE", 0, 4, "CREATURE")
        try:
            self.restAspect.searchAssets( "WRONG_VALUE", 0, 4, "CREATURE")
        except ValueError, error:
            self.assertEquals(
                error.message,
                ("'WRONG_VALUE' is not one of 'TOP_RATED', 'TOP_RATED_NEW', "
                 "'NEWEST', 'FEATURED', 'MAXIS_MADE', 'RANDOM', "
                 "'CUTE_AND_CREEPY'"))

    def test_searchAssetsInvalidAssetType(self):

        self.assertRaises(ValueError, self.restAspect.searchAssets, 
                          "TOP_RATED", 0, 4, "WRONG_VALUE")
        try:
            self.restAspect.searchAssets("TOP_RATED", 0, 4, "WRONG_VALUE")
        except ValueError, error:
            self.assertEquals(
                error.message,
                ("'WRONG_VALUE' is not one of 'UFO', 'CREATURE', 'BUILDING', "
                 "'VEHICLE'"))


class StaticDataAspectTestCase(TXSporeTestCase):

    def setUp(self):
        super(StaticDataAspectTestCase, self).setUp()
        self.client = client.AsyncClient()
        self.dataAspect = self.client.data

    def test_blockingSave(self):
        filename = self.dataAspect._blockingSave(
            "some data", self.tempDirname, self.tempBasename)
        self.assertEquals(filename, "%s/%s" % (
            self.tempDirname, self.tempBasename))
        self.assertEquals(self.tempFilePath.getContent(), "some data")

    def test_saveFile(self):

        def checkFileContents(filename):
            self.assertEquals(filename, self.tempFilePath.path)
            self.assertEquals(
                self.tempFilePath.getContent(), "test payload data")

        d = self.dataAspect._saveFile(
            "test payload data", self.tempDirname, self.tempBasename)
        d.addCallback(checkFileContents)
        return d

    def test_saveToFileDescriptor(self):

        fd = StringIO()

        def checkFileContents(ignored):
            self.assertEquals(
                fd.getvalue(), "test payload data")

        d = self.dataAspect._saveToFileDescriptor(
            "test payload data", fd=fd)
        d.addCallback(checkFileContents)
        return d

    # XXX even though this test is passing, it's not really working.
    # something's wrong and needs to be figured out...
    def test_saveFileWithError(self):

        def raiseError(data, path, filename):
            raise IOError("thread oops")

        self.addCleanup(setattr, self.dataAspect, "_blockingSave",
                        self.dataAspect._blockingSave)
        client._blockingSave = raiseError
        self.addCleanup(setattr, client, "deferToThread", client.deferToThread)
        threadPool = ThreadPool(0, 1)
        threadPool.start()
        self.addCleanup(threadPool.stop)
        client.deferToThread = partial(deferToThreadPool, reactor, threadPool)

        def checkError(error, catcher):
            pass
            #import pdb;pdb.set_trace()

        d = self.dataAspect._saveFile("data", "path", "filename")
        d.addErrback(checkError, self.catcher)
        #self.assertFailure(d, IOError)
        #errors = self.flushLoggedErrors(IOError)
        #self.assertEquals(errors, "XX")
        #self.assertEquals(self.catcher, "")
        #logged = self.catcher.pop()
        #self.assertEquals(logged["message"][0], "ERROR: oops")

    def test_fetchAndSave(self):

        def checkFileContents(filename):
            self.assertEquals(filename, self.tempFilePath.path)
            self.assertEquals(
                self.tempFilePath.getContent(),
                "\nsampleStaticDataLargeCardResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataLargeCardResponse)

        d = self.dataAspect._fetchAndSave(
            "http://some.spore.url", self.tempBasename, self.tempDirname)
        d.addCallback(checkFileContents)
        return d

    def test_fetchAndSaveWithFileDescriptor(self):

        fd = StringIO()

        def checkFileContents(ignored):
            self.assertEquals(
                fd.getvalue(),
                "\nsampleStaticDataLargeCardResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataLargeCardResponse)

        d = self.dataAspect._fetchAndSave(
            "http://some.spore.url", fd=fd)
        d.addCallback(checkFileContents)
        return d

    def test_getLargeCard(self):

        def checkFileContents(filename, assetID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s_lrg_card.png" % assetID
            self.assertEquals(fp.basename(), expectedFilename)
            self.assertEquals(
                fp.getContent(),
                "\nsampleStaticDataLargeCardResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataLargeCardResponse)

        assetID = "500327625969"
        d = self.dataAspect.getLargeCard(assetID, self.tempDirname)
        d.addCallback(checkFileContents, assetID)
        return d

    def test_getAssetDataXML(self):

        def checkFileContents(filename, assetID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s.xml" % assetID
            self.assertEquals(fp.basename(), expectedFilename)
            xmlTree = util.XML(fp.getContent())
            assetModel = model.RecursiveDataModel(xmlTree)
            self.assertEquals(len(assetModel.blocks), 58)
            self.assertEquals(len(assetModel.blocks[1].childlist), 9)
            self.assertEquals(assetModel.blocks[0].transform.scale, 0.786903)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataAssetDataXMLResponse)

        assetID = "500327625969"
        d = self.dataAspect.getAssetDataXML(assetID, self.tempDirname)
        d.addCallback(checkFileContents, assetID)
        return d

    def test_getAssetDataLargePNG(self):

        def checkFileContents(filename, assetID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s_lrg.png" % assetID
            self.assertEquals(fp.basename(), expectedFilename)
            self.assertEquals(
                fp.getContent(),
                "\nsampleStaticDataAssetDataLargePNGResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataAssetDataLargePNGResponse)

        assetID = "500327625969"
        d = self.dataAspect.getAssetDataLargePNG(assetID, self.tempDirname)
        d.addCallback(checkFileContents, assetID)
        return d

    def test_getAssetDataSmallPNG(self):

        def checkFileContents(filename, assetID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s.png" % assetID
            self.assertEquals(fp.basename(), expectedFilename)
            self.assertEquals(
                fp.getContent(),
                "\nsampleStaticDataAssetDataSmallPNGResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataAssetDataSmallPNGResponse)

        assetID = "500327625969"
        d = self.dataAspect.getAssetDataSmallPNG(assetID, self.tempDirname)
        d.addCallback(checkFileContents, assetID)
        return d

    def test_getAchievementIcon(self):

        def checkFileContents(filename, achievmentID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s.png" % achievmentID
            self.assertEquals(fp.basename(), expectedFilename)
            self.assertEquals(
                fp.getContent(),
                "\nsampleStaticDataAchievementIconResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataAchievementIconResponse)

        achievmentID = "someid"
        d = self.dataAspect.getAchievementIcon(achievmentID, self.tempDirname)
        d.addCallback(checkFileContents, achievmentID)
        return d

    def test_getAchievementText(self):

        def checkFileContents(filename, basename):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s.xml" % basename
            self.assertEquals(fp.basename(), expectedFilename)
            xmlTree = util.XML(fp.getContent())
            achievementsModel = model.RecursiveDataModel(xmlTree)
            self.assertEquals(len(achievementsModel.achievements), 124)
            self.assertEquals(
                achievementsModel.achievements[123].name, "Social")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataAchievementDataXMLResponse)

        basename = "achievements"
        d = self.dataAspect.getAchievementDataXML(self.tempDirname)
        d.addCallback(checkFileContents, basename)
        return d

    def test_getPartInfo(self):

        def checkFileContents(filename, blockType):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%sblockmap.xml" % blockType
            self.assertEquals(fp.basename(), expectedFilename)
            xmlTree = util.XML(fp.getContent())
            partsModel = model.RecursiveDataModel(xmlTree)
            self.assertEquals(len(partsModel.blocks), 252)
            self.assertEquals(
                partsModel.blocks[251].name, "Polygon Window")
            self.assertEquals(
                partsModel.blocks[251].type, "Window")
            self.assertEquals(
                partsModel.blocks[251].cost, 500)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataBuildingBlockMapPartInfoResponse)

        blockType = "building"
        d = self.dataAspect.getPartInfo(blockType, self.tempDirname)
        d.addCallback(checkFileContents, blockType)
        return d

    def test_getPartInfoInvalidInput(self):

        self.assertRaises(ValueError, self.dataAspect.getPartInfo,
                                 "something crazy", self.tempDirname)
        try:
            self.dataAspect.getPartInfo("something crazy", self.tempDirname)
        except ValueError, error:
            self.assertEquals(
                error.message,
                ("'something crazy' is not one of 'creature', 'limb', "
                 "'building', 'vehicle', ''"))

    def test_getPartIcon(self):

        def checkFileContents(filename, assetID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s.png" % assetID
            self.assertEquals(fp.basename(), expectedFilename)
            self.assertEquals(
                fp.getContent(),
                "\nsampleStaticDataPartIconResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataPartIconResponse)

        partFilename = "ce_grasper_radial_02"
        d = self.dataAspect.getPartIcon(partFilename, self.tempDirname)
        d.addCallback(checkFileContents, partFilename)
        return d

    def test_getPaintInfo(self):

        def checkFileContents(filename, basename):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s.xml" % basename
            self.assertEquals(fp.basename(), expectedFilename)
            xmlTree = util.XML(fp.getContent())
            paintsModel = model.RecursiveDataModel(xmlTree)
            self.assertEquals(len(paintsModel.paints), 552)
            self.assertEquals(
                paintsModel.paints[104].filename, "be_concrete_06")
            self.assertEquals(
                paintsModel.paints[104].aestheticTags, ["stucco", "stone"])

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataPaintInfoResponse)

        basename = "paintmap"
        d = self.dataAspect.getPaintInfo(self.tempDirname)
        d.addCallback(checkFileContents, basename)
        return d

    def test_getPaintIcon(self):

        def checkFileContents(filename, assetID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s.png" % assetID
            self.assertEquals(fp.basename(), expectedFilename)
            self.assertEquals(
                fp.getContent(),
                "\nsampleStaticDataPaintIconResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataPaintIconResponse)

        partFilename = "ce_grasper_radial_02"
        d = self.dataAspect.getPaintIcon(partFilename, self.tempDirname)
        d.addCallback(checkFileContents, partFilename)
        return d


class AtomAspectTestCase(TXSporeTestCase):

    def setUp(self):
        super(AtomAspectTestCase, self).setUp()
        self.client = client.AsyncClient()
        self.atomAspect = self.client.atom

    def test_getXMLForAtom(self):

        def checkForXML(result):
            children = [util.scrubXMLNameSpace(x.tag) for x in result]
            expected = ["id", "title", "updated", "link", "entry", "entry"]
            self.assertEquals(children, expected)
            self.assertEquals(util.scrubXMLNameSpace(result.tag), "feed")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleAtomEventsForAssetResponse)

        d = self.atomAspect._getXMLForAtom("http://some.spore.url")
        d.addCallback(checkForXML)
        return d

    def test_getAssetsForUser(self):

        def checkModel(atomModel):
            self.assertEquals(atomModel.title, "oubiwann")
            self.assertEquals(atomModel.updated,
                datetime(2009, 9, 11, 2, 15, 46))
            self.assertEquals(atomModel.link.href,
                "http://www.spore.com/atom/user/2263046854")
            self.assertEquals(len(atomModel.entries), 349)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleAtomAssetsForUserResponse)

        d = self.atomAspect.getAssetsForUser("oubiwann")
        d.addCallback(checkModel)
        return d

    def test_getEventsForUser(self):

        def checkModel(atomModel):
            self.assertEquals(atomModel.title, "Spore Event Feed")
            self.assertEquals(atomModel.updated,
                datetime(2009, 9, 16, 6, 19, 40))
            self.assertEquals(atomModel.link.href,
                "http://www.spore.comnull/atom/communityEvent/null")
            self.assertEquals(len(atomModel.entries), 20)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleAtomEventsForUserResponse)

        d = self.atomAspect.getEventsForUser("oubiwann")
        d.addCallback(checkModel)
        return d

    def test_getEventsForAsset(self):

        def checkModel(atomModel):
            self.assertEquals(atomModel.title, "Spore Event Feed")
            self.assertEquals(atomModel.updated,
                datetime(2009, 9, 16, 6, 19, 40))
            self.assertEquals(atomModel.link.href,
                "http://www.spore.comnull/atom/communityEvent/null")
            self.assertEquals(len(atomModel.entries), 2)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleAtomEventsForAssetResponse)

        d = self.atomAspect.getEventsForAsset("someasset")
        d.addCallback(checkModel)
        return d

    def test_getSporeCastFeed(self):

        def checkModel(atomModel):
            self.assertEquals(atomModel.title, "Nice Guys")
            self.assertEquals(atomModel.updated,
                datetime(2009, 6, 29, 14, 33, 22))
            self.assertEquals(atomModel.link.href,
                "http://www.spore.com/atom/aggregator/500320272789")
            self.assertEquals(len(atomModel.entries), 14)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleAtomSporeCastFeedResponse)

        d = self.atomAspect.getSporeCastFeed("somesporecastid")
        d.addCallback(checkModel)
        return d

    def test_searchAssets(self):

        def checkModel(atomModel):
            self.assertEquals(atomModel.title, "Searched Assets")
            self.assertEquals(atomModel.updated,
                datetime(2009, 9, 10, 23, 22, 51))
            self.assertEquals(atomModel.link.href,
                "http://www.spore.com/atom/asset/null")
            self.assertEquals(len(atomModel.entries), 5)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleAtomAssetSearchResponse)

        d = self.atomAspect.searchAssets("MAXIS_MADE", 0, 5)
        d.addCallback(checkModel)
        return d


class ClientTestCase(TXSporeTestCase):

    def test_creation(self):
        asyncClient = AsyncClient()
        self.assertTrue(isinstance(asyncClient.rest, client.RESTAspect))
        self.assertTrue(isinstance(asyncClient.data, client.StaticDataAspect))
        self.assertTrue(isinstance(asyncClient.cache, client.Cache))

    def test_setCache(self):
        asyncClient = AsyncClient()
        asyncClient._setCache("some data", "http://a.url/thing")
        self.assertEquals(
            asyncClient.cache.get("http://a.url/thing"), "some data")

    def test_openURL(self):
        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleStaticDataLargeCardResponse)

        asyncClient = AsyncClient()
        d = asyncClient.openURL("http://some.spore.url")
        d.addCallback(
            self.assertEquals,
            "\nsampleStaticDataLargeCardResponse BINARY DATA")
        return d

    def test_openURLWithError(self):
        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: fail(ValueError("oops"))

        def checkLog(ignored):
            logged = self.catcher.pop()
            self.assertEquals(logged["message"][0], "ERROR: oops")

        asyncClient = AsyncClient()
        failure = asyncClient.openURL("http://some.spore.url/")
        d = self.assertFailure(failure, ValueError)
        d.addCallback(checkLog)
        return d

    def test_openURLCached(self):
        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed("request 1")

        def checkGetPage2(result2):
            self.assertEquals(result2, "request 1")

        def checkGetPage1(result1, asyncClient):
            self.assertEquals(result1, "request 1")
            client.getPage = lambda url: succeed("request 2")
            d = asyncClient.openURL("http://some.spore.url/")
            d.addCallback(checkGetPage2)

        asyncClient = AsyncClient()
        d = asyncClient.openURL("http://some.spore.url/")
        d.addCallback(checkGetPage1, asyncClient)
        return d

    def test_openURLSkipCache(self):
        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed("request 1")

        def checkGetPage2(result2):
            self.assertEquals(result2, "request 2")

        def checkGetPage1(result1, asyncClient):
            self.assertEquals(result1, "request 1")
            client.getPage = lambda url: succeed("request 2")
            d = asyncClient.openURL("http://some.spore.url/", skipCache=True)
            d.addCallback(checkGetPage2)

        asyncClient = AsyncClient()
        d = asyncClient.openURL("http://some.spore.url/")
        d.addCallback(checkGetPage1, asyncClient)
        return d
