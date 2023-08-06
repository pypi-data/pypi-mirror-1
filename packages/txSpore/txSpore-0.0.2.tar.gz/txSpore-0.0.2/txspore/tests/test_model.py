from datetime import datetime

from twisted.trial.unittest import TestCase

from txspore import model
from txspore.testing import payload
from txspore.util import XML


class ParsingModelTestCase(TestCase):

    def setUp(self):
        super(ParsingModelTestCase, self).setUp()
        self.xmlTree = XML(
            "<xml><data>some data</data>"
            "<float>3.14159</float><integer>42</integer>"
            "<notFloat>1.a</notFloat><null>NULL</null>"
            "<tags>[apple, banana, cranberry]</tags>"
            "<date>1999-12-31 23:59:59</date></xml>")
        self.model = model.ParsingModel(self.xmlTree)

    def test_creation(self):
        self.assertEquals(self.model.data, "some data")
        self.assertEquals(self.model.float, 3.14159)
        self.assertEquals(self.model.integer, 42)
        self.assertEquals(self.model.notFloat, "1.a")
        self.assertEquals(self.model.null, "")
        self.assertEquals(self.model.tags, ["apple", "banana", "cranberry"])
        self.assertEquals(self.model.date, datetime(1999, 12, 31, 23, 59, 59))

    def test_hasChildren(self):
        self.assertTrue(self.model.hasChildren(self.xmlTree))
        self.assertFalse(self.model.hasChildren(self.xmlTree.find("float")))

    def test_parseNodes(self):
        xmlBytes = "<xml><attribute>some data</attribute></xml>"
        node = XML(xmlBytes)
        parsingModel = model.ParsingModel()
        parsingModel.parseNodes(node)
        self.assertEquals(parsingModel.attribute, "some data")

    def test_parseNodesDate(self):
        self.assertEquals(
            self.model.date.strftime("%Y-%m-%d %T"),
            "1999-12-31 23:59:59")

    def test_parseNodesNumbers(self):
        self.assertTrue(isinstance(self.model.float, float))
        self.assertTrue(isinstance(self.model.integer, int))
        self.assertTrue(isinstance(self.model.notFloat, str))

    def test_parseNodesListTypes(self):
        self.assertEquals(self.model.tags, ["apple", "banana", "cranberry"])
        xmlTree = XML("<xml><tags>NULL</tags></xml>")
        emptyTags = model.ParsingModel(xmlTree)
        self.assertEquals(emptyTags.tags, [])


class DailyStatsTestCase(TestCase):

    def setUp(self):
        super(DailyStatsTestCase, self).setUp()
        self.xmlTree = XML(payload.sampleRESTDailyStatsResponse)
        self.dailyStats = model.DailyStats(self.xmlTree)

    def test_creation(self):
        self.assertEquals(self.dailyStats.totalUploads, 121325142)
        self.assertEquals(self.dailyStats.dayUploads, 88683)
        self.assertEquals(self.dailyStats.totalUsers, 3055769)
        self.assertEquals(self.dailyStats.dayUsers, 1235)


class CreatureStatsTestCase(TestCase):

    def setUp(self):
        super(CreatureStatsTestCase, self).setUp()
        self.xmlTree = XML(payload.sampleRESTCreatureStatsResponse)
        self.creatureStats = model.CreatureStats(self.xmlTree)

    def test_creation(self):
        self.assertEquals(self.creatureStats.status, 1)
        self.assertEquals(self.creatureStats.input, 500327625969)
        self.assertEquals(self.creatureStats.cost, 1925)
        self.assertEquals(self.creatureStats.health, 5.0)
        self.assertEquals(self.creatureStats.height, 0.99036040)
        self.assertEquals(self.creatureStats.meanness, 20.0)
        self.assertEquals(self.creatureStats.cuteness, 18.330488)
        self.assertEquals(self.creatureStats.sense, 1.0)
        self.assertEquals(self.creatureStats.bonecount, 43.0)
        self.assertEquals(self.creatureStats.footcount, 4.0)
        self.assertEquals(self.creatureStats.graspercount, 0.0)
        self.assertEquals(self.creatureStats.basegear, 0.0)
        self.assertEquals(self.creatureStats.carnivore, 1.0)
        self.assertEquals(self.creatureStats.herbivore, 1.0)
        self.assertEquals(self.creatureStats.glide, 0.0)
        self.assertEquals(self.creatureStats.sprint, 3.0)
        self.assertEquals(self.creatureStats.stealth, 0.0)
        self.assertEquals(self.creatureStats.bite, 1.0)
        self.assertEquals(self.creatureStats.charge, 4.0)
        self.assertEquals(self.creatureStats.strike, 0.0)
        self.assertEquals(self.creatureStats.spit, 0.0)
        self.assertEquals(self.creatureStats.sing, 1.0)
        self.assertEquals(self.creatureStats.dance, 0.0)
        self.assertEquals(self.creatureStats.gesture, 0.0)
        self.assertEquals(self.creatureStats.posture, 0.0)

    def test_parseNodes(self):
        xmlBytes = "<creature><attribute>3.14159</attribute></creature>"
        node = XML(xmlBytes)
        stats = model.CreatureStats()
        stats.parseNodes(node)
        self.assertEquals(stats.attribute, 3.14159)


class UserTestCase(TestCase):

    def setUp(self):
        super(UserTestCase, self).setUp()
        self.xmlTree = XML(payload.sampleRESTProfileInfoResponse)
        self.user = model.User(self.xmlTree)

    def test_creation(self):
        self.assertEquals(self.user.status, 1)
        self.assertEquals(self.user.input, "oubiwann")
        self.assertEquals(self.user.id, 2263046854)
        self.assertEquals(
            self.user.image,
            "http://www.spore.com/static/thumb/500/327/695/500327695945.png")
        self.assertEquals(self.user.tagline, "")
        self.assertEquals(self.user.creation, datetime(2008, 6, 17, 18, 45))


class AssetsForUserTestCase(TestCase):

    def setUp(self):
        super(AssetsForUserTestCase, self).setUp()
        parentNode = XML(payload.sampleRESTAssetsForUserResponse)
        self.xmlNode = parentNode.find("asset")
        self.asset = model.Asset(self.xmlNode)

    def test_creation(self):
        self.assertEquals(self.asset.id, 500447356422)
        self.assertEquals(self.asset.name, "Borziadinid")
        self.assertEquals(
            self.asset.thumb,
            "http://www.spore.com/static/thumb/500/447/356/500447356422.png")
        self.assertEquals(
            self.asset.image,
            "http://www.spore.com/static/image/500/447/356/500447356422_lrg.png")
        self.assertEquals(self.asset.created, datetime(2009, 9, 11, 2, 15, 46))
        self.assertEquals(self.asset.rating, -1.0)
        self.assertEquals(self.asset.type, "CREATURE")
        self.assertEquals(self.asset.subtype, "0x4178b8e8")
        self.assertEquals(self.asset.parent, 500438942899)
        self.assertEquals(self.asset.description, "")
        self.assertEquals(self.asset.tags, [])


class SporeCastTestCase(TestCase):

    def setUp(self):
        super(SporeCastTestCase, self).setUp()
        parentNode = XML(payload.sampleRESTSporeCastsForUserResponse)
        self.xmlNode = parentNode.find("sporecast")
        self.sporecast = model.SporeCast(self.xmlNode)

    def test_creation(self):
        self.assertEquals(self.sporecast.title, "Clark and Stanley")
        self.assertEquals(
            self.sporecast.subtitle,
            "Clark and stanley missions for GA")
        self.assertEquals(self.sporecast.id, 500384059016)
        self.assertEquals(self.sporecast.author, "1234ummm6")
        self.assertEquals(
            self.sporecast.updated,
            datetime(2009, 7, 1, 15, 10, 50))
        self.assertEquals(self.sporecast.rating, 8.0)
        self.assertEquals(self.sporecast.subscriptioncount, 67)
        self.assertEquals(self.sporecast.tags, [])
        self.assertEquals(self.sporecast.count, 69)


class SporeCastAssetTestCase(TestCase):

    def setUp(self):
        super(SporeCastAssetTestCase, self).setUp()
        parentNode = XML(payload.sampleRESTAssetsForSporeCastResponse)
        self.xmlNode = parentNode.find("asset")
        self.asset = model.Asset(self.xmlNode)

    def test_creation(self):
        self.assertEquals(self.asset.id, 500378366841)
        self.assertEquals(self.asset.name, "Mountain Nurble")
        self.assertEquals(
            self.asset.thumb,
            "http://www.spore.com/static/thumb/500/378/366/500378366841.png")
        self.assertEquals(
            self.asset.image,
            "http://www.spore.com/static/image/500/378/366/500378366841_lrg.png")
        self.assertEquals(self.asset.created, datetime(2009, 6, 26, 21, 7, 38))
        self.assertEquals(self.asset.rating, -1.0)
        self.assertEquals(self.asset.type, "CREATURE")
        self.assertEquals(self.asset.subtype, "0x9ea3031a")
        self.assertEquals(self.asset.parent, 500371338603)
        self.assertEquals(self.asset.description, "")
        self.assertEquals(self.asset.tags, [])


class AchievementTestCase(TestCase):

    def setUp(self):
        super(AchievementTestCase, self).setUp()
        parentNode = XML(payload.sampleRESTAchievementsForUserResponse)
        self.xmlNode = parentNode.find("achievement")
        self.achievement = model.Achievement(self.xmlNode)

    def test_creation(self):
        self.assertEquals(self.achievement.guid, "0xaec66642!0x0770b845")
        self.assertEquals(
            self.achievement.date.strftime("%Y-%m-%d %T"),
            "2009-08-09 18:10:35")


class AssetTestCase(TestCase):

    def setUp(self):
        super(AssetTestCase, self).setUp()
        self.xmlNode = XML(payload.sampleRESTInfoForAssetResponse)
        self.asset = model.AssetInfo(self.xmlNode)

    def test_creation(self):
        self.assertEquals(self.asset.status, 1)
        self.assertEquals(self.asset.input, 500327625969)
        self.assertEquals(self.asset.name, "Durnipin")
        self.assertEquals(self.asset.author, "oubiwann")
        self.assertEquals(self.asset.authorid, 2263046854)
        self.assertEquals(
            self.asset.created, datetime(2009, 4, 26, 22, 48, 12))
        self.assertEquals(self.asset.description, "")
        self.assertEquals(self.asset.tags, ["turtle", "tortoise", "terepin"])
        self.assertEquals(self.asset.type, "CREATURE")
        self.assertEquals(self.asset.subtype, "0x9ea3031a")
        self.assertEquals(self.asset.rating, -1.0)
        self.assertEquals(self.asset.parent, 500327615572)
        self.assertEquals(len(self.asset.comments), 2)
        self.assertEquals(self.asset.comments[0].sender, "oubiwann")
        self.assertEquals(
            self.asset.comments[1].message,
            "This comment is used for testing the API")


class CommentTestCase(TestCase):

    def setUp(self):
        super(CommentTestCase, self).setUp()
        parentNode = XML(payload.sampleRESTCommentsForAssetResponse)
        self.xmlNode = parentNode.find("comment")
        self.comment = model.Comment(self.xmlNode)

    def test_creation(self):
        expected_message = (
            "This is a second comment for testing the API (Twisted Python "
            "async Spore API).")
        self.assertEquals(self.comment.message, expected_message)
        self.assertEquals(self.comment.sender, "oubiwann")
        self.assertEquals(
            self.comment.date.strftime("%Y-%m-%d %T"),
            "2009-09-12 04:03:22")


class BuddyTestCase(TestCase):

    def setUp(self):
        super(BuddyTestCase, self).setUp()
        parentNode = XML(payload.sampleRESTBuddiesForUserResponse)
        self.xmlNode = parentNode.find("buddy")
        self.asset = model.Buddy(self.xmlNode)

    def test_creation(self):
        self.assertEquals(self.asset.name, "Azulon")
        self.assertEquals(self.asset.id, 2260775701)


class SearchAssetTestCase(TestCase):

    def setUp(self):
        super(SearchAssetTestCase, self).setUp()
        parentNode = XML(payload.sampleRESTAssetSearchResponse)
        self.xmlNode = parentNode.find("asset")
        self.asset = model.Asset(self.xmlNode)

    def test_creation(self):
        self.assertEquals(self.asset.id, 500447216760)
        self.assertEquals(self.asset.name, "Goring")
        self.assertEquals(
            self.asset.thumb,
            "http://www.spore.com/static/thumb/500/447/216/500447216760.png")
        self.assertEquals(
            self.asset.image,
            "http://www.spore.com/static/image/500/447/216/500447216760_lrg.png")
        self.assertEquals(self.asset.created, datetime(2009, 9, 10, 22, 0, 51))
        self.assertEquals(self.asset.rating, 1.5000005)
        self.assertEquals(self.asset.type, "CREATURE")
        self.assertEquals(self.asset.subtype, "0x9ea3031a")
        self.assertEquals(self.asset.parent, "")
        self.assertEquals(self.asset.description, "")
        self.assertEquals(self.asset.tags, [])


class StaticAssetDataTestCase(TestCase):

    def setUp(self):
        super(StaticAssetDataTestCase, self).setUp()
        self.xmlTree = XML(payload.sampleStaticDataAssetDataXMLResponse)
        self.assetData = model.RecursiveDataModel(self.xmlTree)

    def test_creation(self):
        self.assertEquals(self.assetData.getName(), "Sporemodel")
        self.assertEquals(self.assetData.formatversion, 16)
        self.assertEquals(
            self.assetData.properties.skincolor1,
            "0.431372,0.800000,0.400000")
        self.assertEquals(self.assetData.properties.skineffectseed1, 1234)
        self.assertEquals(len(self.assetData.blocks), 58)
        self.assertEquals(
            self.assetData.blocks[0].blockid, "0x40626000, 0xd05c53a3")
        self.assertEquals(self.assetData.blocks[0].snapped, "false")
        self.assertEquals(len(self.assetData.blocks[0].childlist), 1)
        self.assertEquals(self.assetData.blocks[0].transform.scale, 0.786903)
        self.assertEquals(
            self.assetData.blocks[0].transform.position,
            "0,0.505799,0.229491")
        self.assertEquals(
            self.assetData.blocks[0].transform.orientation.row0,
            "1.000000,0,0")
        self.assertEquals(len(self.assetData.blocks[1].childlist), 9)
        self.assertEquals(self.assetData.blocks[1].childlist[1], 35)
        self.assertEquals(self.assetData.blocks[1].childlist[8], 2)
        self.assertEquals(
            self.assetData.blocks[23].blockid, "0x40626000, 0x559876a9")
        self.assertEquals(
            self.assetData.blocks[57].blockid, "0x40626000, 0x631d0fee")


class AchievementsDataTestCase(TestCase):

    def setUp(self):
        super(AchievementsDataTestCase, self).setUp()
        self.xmlTree = XML(payload.sampleStaticDataAchievementDataXMLResponse)
        self.achivementsData = model.RecursiveDataModel(self.xmlTree)

    def test_creation(self):
        self.assertEquals(len(self.achivementsData.achievements), 124)
        self.assertEquals(
            self.achivementsData.achievements[0].id, "0x0cc8b2c9!0x7e1737dc")
        self.assertEquals(
            self.achivementsData.achievements[0].name, "Spore Addict")
        self.assertEquals(
            self.achivementsData.achievements[0].description,
            "Spend 100 hours in your Spore galaxy")
        self.assertEquals(
            self.achivementsData.achievements[123].id, "0x9a5acf10!0x00000147")
        self.assertEquals(
            self.achivementsData.achievements[123].name, "Social")
        self.assertEquals(
            self.achivementsData.achievements[123].description,
            ("Social creatures are constantly searching for new friends "
             "and allies.  Meeting a new species is the highlight of their "
             "day."))


class PartInfoTestCase(TestCase):

    def setUp(self):
        super(PartInfoTestCase, self).setUp()
        self.xmlTree = XML(
            payload.sampleStaticDataBuildingBlockMapPartInfoResponse)
        self.partData = model.RecursiveDataModel(self.xmlTree)

    def test_creation(self):
        self.assertEquals(len(self.partData.blocks), 252)
        self.assertEquals(
            self.partData.blocks[0].id, "0xcce7e453")
        self.assertEquals(
            self.partData.blocks[0].name, "Barn Roof")
        self.assertEquals(
            self.partData.blocks[0].type, "Roof")
        self.assertEquals(
            self.partData.blocks[0].cost, 500)
        self.assertEquals(
            self.partData.blocks[251].id, "0xd96e47f1")
        self.assertEquals(
            self.partData.blocks[251].name, "Polygon Window")
        self.assertEquals(
            self.partData.blocks[251].type, "Window")
        self.assertEquals(
            self.partData.blocks[251].cost, 500)


class PaintInfoTestCase(TestCase):

    def setUp(self):
        super(PaintInfoTestCase, self).setUp()
        self.xmlTree = XML(payload.sampleStaticDataPaintInfoResponse)
        self.paintData = model.RecursiveDataModel(self.xmlTree)

    def test_creation(self):
        self.assertEquals(len(self.paintData.paints), 552)
        self.assertEquals(
            self.paintData.paints[0].id, "0x35915380")
        self.assertEquals(
            self.paintData.paints[0].filename, "be_airship_13")
        self.assertEquals(
            self.paintData.paints[0].aestheticTags, ["airship"])
        self.assertEquals(
            self.paintData.paints[104].id, "0xb99f5179")
        self.assertEquals(
            self.paintData.paints[104].filename, "be_concrete_06")
        self.assertEquals(
            self.paintData.paints[104].aestheticTags, ["stucco", "stone"])


class AtomDataModelTestCase(TestCase):

    def setUp(self):
        super(AtomDataModelTestCase, self).setUp()
        self.xmlTree = XML(payload.sampleAtomAssetsForUserResponse)
        self.atomData = model.AtomDataModel(self.xmlTree)

    def test_creation(self):
        self.assertEquals(self.atomData.title, "oubiwann")
        self.assertEquals(self.atomData.updated,
            datetime(2009, 9, 11, 2, 15, 46))
        self.assertEquals(self.atomData.link.href,
            "http://www.spore.com/atom/user/2263046854")
        self.assertEquals(len(self.atomData.entries), 349)
        self.assertEquals(self.atomData.entries[0].title, "Borziadinid")
        self.assertEquals(self.atomData.entries[0].updated,
            datetime(2009, 9, 11, 2, 15, 46))
        self.assertEquals(self.atomData.entries[0].author.name, "oubiwann")
        self.assertEquals(self.atomData.entries[0].content.type, "html")
        self.assertEquals(self.atomData.entries[0].content.img.src,
            "http://static.spore.com/static/thumb/500/447/356/500447356422.png")
