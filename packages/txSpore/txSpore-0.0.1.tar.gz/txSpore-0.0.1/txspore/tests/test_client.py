from cStringIO import StringIO
from datetime import datetime
from functools import partial

from twisted.internet import reactor
from twisted.internet.defer import succeed, fail
from twisted.internet.threads import deferToThreadPool
from twisted.python.filepath import FilePath
from twisted.python.threadpool import ThreadPool
from twisted.trial.unittest import SkipTest

from txspore import client
from txspore import model
from txspore import util
from txspore.client import getXMLForREST
from txspore.testing import payload
from txspore.testing.base import TXSporeTestCase


class ClientTestCase(TXSporeTestCase):

    def test_openURL(self):
        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(payload.sampleLargeCardResponse)

        d = client.openURL("http://some.spore.url")
        d.addCallback(
            self.assertEquals, "\nsampleLargeCardResponse BINARY DATA")
        return d

    def test_openURLWithError(self):
        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: fail(ValueError("oops"))

        d = client.openURL("http://some.spore.url")
        self.assertFailure(d, ValueError)
        logged = self.catcher.pop()
        self.assertEquals(logged["message"][0], "ERROR: oops")


class ClientRESTAPITestCase(TXSporeTestCase):

    def setUp(self):
        super(ClientRESTAPITestCase, self).setUp()

    def test_getXMLForRest(self):

        def checkForXML(result):
            children = [x.tag for x in result]
            expected = ['totalUploads', 'dayUploads', 'totalUsers', 'dayUsers']
            self.assertEquals(children, expected)
            self.assertEquals(result.tag, "stats")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(payload.sampleDailyStatsResponse)

        d = getXMLForREST("http://some.spore.url")
        d.addCallback(checkForXML)
        return d

    def test_getXMLForRestWithError(self):
        self.addCleanup(setattr, client, "openURL", client.openURL)
        client.openURL = lambda url: fail(RuntimeError("oops"))

        d = client.getXMLForREST("http://some.spore.url")
        self.assertFailure(d, RuntimeError)
        logged = self.catcher.pop()
        self.assertEquals(logged["message"][0], "ERROR: oops")

    def test_getModulesForSubNodes(self):
        pass

    def test_getDailyStats(self):

        def checkModel(model):
            self.assertEquals(model.totalUploads, 120785568)
            self.assertEquals(model.dayUploads, 117668)
            self.assertEquals(model.totalUsers, 3048497)
            self.assertEquals(model.dayUsers, 1581)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleDailyStatsResponse)

        d = client.getDailyStats()
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
            payload.sampleCreatureStatsResponse)

        d = client.getStatsForCreature("500327625969")
        d.addCallback(checkModel)
        return d

    def test_getProfileInfo(self):

        def checkModel(model):
            self.assertEquals(model.status, 1)
            self.assertEquals(model.input, "oubiwann")
            self.assertEquals(model.id, 2263046854)

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleProfileInfoResponse)

        d = client.getProfileInfo("oubiwann")
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
            payload.sampleAssetsForUserResponse)

        d = client.getAssetsForUser("oubiwann", 0, 4)
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
            payload.sampleSporeCastsForUserResponse)

        d = client.getSporeCastsForUser("oubiwann")
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
            payload.sampleAssetsForSporeCastResponse)

        d = client.getAssetsForSporeCast("oubiwann", 0, 3)
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
            payload.sampleAchievementsForUserResponse)

        d = client.getAchievementsForUser("oubiwann", 0, 2)
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
            payload.sampleInfoForAssetResponse)

        d = client.getInfoForAsset("500327625969")
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
            payload.sampleCommentsForAssetResponse)

        d = client.getCommentsForAsset("500327625969", 0, 2)
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
            payload.sampleBuddiesForUserResponse)

        d = client.getBuddiesForUser("oubiwann", 0, 2)
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
            payload.sampleAssetSearchResponse)

        d = client.searchAssets("MAXIS_MADE", 0, 4, "CREATURE")
        d.addCallback(checkModel)
        return d


class ClientStaticDataOpenAndFetchTestCase(TXSporeTestCase):

    def test_blockingSave(self):
        filename = client.blockingSave(
            "some data", self.tempDirname, self.tempBasename)
        self.assertEquals(filename, "%s/%s" % (
            self.tempDirname, self.tempBasename))
        self.assertEquals(self.tempFilePath.getContent(), "some data")

    def test_saveFile(self):

        def checkFileContents(filename):
            self.assertEquals(filename, self.tempFilePath.path)
            self.assertEquals(
                self.tempFilePath.getContent(), "test payload data")

        d = client.saveFile(
            "test payload data", self.tempDirname, self.tempBasename)
        d.addCallback(checkFileContents)
        return d

    def test_saveToFileDescriptor(self):

        fd = StringIO()

        def checkFileContents(ignored):
            self.assertEquals(
                fd.getvalue(), "test payload data")

        d = client.saveToFileDescriptor(
            "test payload data", fd=fd)
        d.addCallback(checkFileContents)
        return d

    # XXX even though this test is passing, it's not really working.
    # something's wrong and needs to be figured out...
    def test_saveFileWithError(self):

        def raiseError(data, path, filename):
            raise IOError("thread oops")

        self.addCleanup(setattr, client, "blockingSave", client.blockingSave)
        client.blockingSave = raiseError
        self.addCleanup(setattr, client, "deferToThread", client.deferToThread)
        threadPool = ThreadPool(0, 1)
        threadPool.start()
        self.addCleanup(threadPool.stop)
        client.deferToThread = partial(deferToThreadPool, reactor, threadPool)

        def checkError(error, catcher):
            pass
            #import pdb;pdb.set_trace()

        d = client.saveFile("data", "path", "filename")
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
                "\nsampleLargeCardResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(payload.sampleLargeCardResponse)

        d = client.fetchAndSave(
            "http://some.spore.url", self.tempBasename, self.tempDirname)
        d.addCallback(checkFileContents)
        return d

    def test_fetchAndSaveWithFileDescriptor(self):

        fd = StringIO()

        def checkFileContents(ignored):
            self.assertEquals(
                fd.getvalue(), "\nsampleLargeCardResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(payload.sampleLargeCardResponse)

        d = client.fetchAndSave(
            "http://some.spore.url", fd=fd)
        d.addCallback(checkFileContents)
        return d


class ClientStaticDataAPITestCase(TXSporeTestCase):

    def test_getLargeCard(self):

        def checkFileContents(filename, assetID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s_lrg_card.png" % assetID
            self.assertEquals(fp.basename(), expectedFilename)
            self.assertEquals(
                fp.getContent(),
                "\nsampleLargeCardResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(payload.sampleLargeCardResponse)

        assetID = "500327625969"
        d = client.getLargeCard(assetID, self.tempDirname)
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
            payload.sampleAssetDataXMLResponse)

        assetID = "500327625969"
        d = client.getAssetDataXML(assetID, self.tempDirname)
        d.addCallback(checkFileContents, assetID)
        return d

    def test_getAssetDataLargePNG(self):

        def checkFileContents(filename, assetID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s_lrg.png" % assetID
            self.assertEquals(fp.basename(), expectedFilename)
            self.assertEquals(
                fp.getContent(), "\nsampleAssetDataLargePNGResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleAssetDataLargePNGResponse)

        assetID = "500327625969"
        d = client.getAssetDataLargePNG(assetID, self.tempDirname)
        d.addCallback(checkFileContents, assetID)
        return d

    def test_getAssetDataSmallPNG(self):

        def checkFileContents(filename, assetID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s.png" % assetID
            self.assertEquals(fp.basename(), expectedFilename)
            self.assertEquals(
                fp.getContent(), "\nsampleAssetDataSmallPNGResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleAssetDataSmallPNGResponse)

        assetID = "500327625969"
        d = client.getAssetDataSmallPNG(assetID, self.tempDirname)
        d.addCallback(checkFileContents, assetID)
        return d

    def test_getAchievementIcon(self):
        raise SkipTest("Not implemented yet.")

    def test_getAchievementText(self):

        def checkFileContents(filename, basename):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s.xml" % basename
            self.assertEquals(fp.basename(), expectedFilename)
            xmlTree = util.XML(fp.getContent())
            achivementsModel = model.RecursiveDataModel(xmlTree)
            self.assertEquals(len(achivementsModel.achievements), 124)
            self.assertEquals(
                achivementsModel.achievements[123].name, "Social")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.sampleAchievementDataXMLResponse)

        basename = "achievements"
        d = client.getAchievementDataXML(self.tempDirname)
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
            payload.sampleBuildingBlockMapPartInfoResponse)

        blockType = "building"
        d = client.getPartInfo(blockType, self.tempDirname)
        d.addCallback(checkFileContents, blockType)
        return d

    def test_getPartIcon(self):

        def checkFileContents(filename, assetID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s.png" % assetID
            self.assertEquals(fp.basename(), expectedFilename)
            self.assertEquals(
                fp.getContent(), "\nsamplePartIconResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.samplePartIconResponse)

        partFilename = "ce_grasper_radial_02"
        d = client.getPartIcon(partFilename, self.tempDirname)
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
            payload.samplePaintInfoResponse)

        basename = "paintmap"
        d = client.getPaintInfo(self.tempDirname)
        d.addCallback(checkFileContents, basename)
        return d

    def test_getPaintIcon(self):

        def checkFileContents(filename, assetID):
            fp = FilePath(filename)
            self.assertTrue(fp.isfile())
            expectedFilename = "%s.png" % assetID
            self.assertEquals(fp.basename(), expectedFilename)
            self.assertEquals(
                fp.getContent(), "\nsamplePaintIconResponse BINARY DATA")

        self.addCleanup(setattr, client, "getPage", client.getPage)
        client.getPage = lambda url: succeed(
            payload.samplePaintIconResponse)

        partFilename = "ce_grasper_radial_02"
        d = client.getPaintIcon(partFilename, self.tempDirname)
        d.addCallback(checkFileContents, partFilename)
        return d


