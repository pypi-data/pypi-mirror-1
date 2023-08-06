from twisted.python.failure import Failure

from txspore import util
from txspore.testing.base import TXSporeTestCase


class LogTestCase(TXSporeTestCase):

    def test_logError(self):
        error = Failure(IndexError("oops"))
        self.assertRaises(IndexError, util.logError, error)
        logged = self.catcher.pop()
        self.assertEquals(logged["message"][0], "ERROR: oops")

    def test_logErrorWithOverride(self):
        error = Failure(IndexError("oops"))
        self.assertRaises(ValueError, util.logError, error, ValueError)
        logged = self.catcher.pop()
        self.assertEquals(logged["message"][0], "ERROR: oops")

    def test_logErrorWithMessage(self):
        error = Failure(IndexError("oops"))
        self.assertRaises(IndexError, util.logError, error,
                          message="oh noes")
        logged = self.catcher.pop()
        self.assertEquals(logged["message"][0], "ERROR: oh noes")

    def test_logErrorWithOverrideAndMessage(self):
        error = Failure(IndexError("oops"))
        self.assertRaises(ValueError, util.logError, error, ValueError,
                          "oh noes")
        logged = self.catcher.pop()
        self.assertEquals(logged["message"][0], "ERROR: oh noes")


class UtilTestCase(TXSporeTestCase):

    def test_XML(self):
        xmlBytes = "<xml><something>xml data</something></xml>"
        node = util.XML(xmlBytes)
        data = node.findtext("something")
        self.assertEquals(data, "xml data")

    def test_XMLWithSpaces(self):
        xmlBytes = "   <xml><something>xml data</something></xml>   "
        node = util.XML(xmlBytes)
        data = node.findtext("something")
        self.assertEquals(data, "xml data")

    def test_parseXMLDate(self):
        date = "2009-09-12 04:03:22.783"
        datetime = util.parseXMLDate(date)
        self.assertEquals(datetime.strftime("%Y-%m-%d %T"), date.split(".")[0])

    def test_stringToList(self):
        self.assertEquals(util.stringToList("[]"), [])
        self.assertEquals(util.stringToList("[apple]"), ["apple"])
        self.assertEquals(util.stringToList("[  apple  ]"), ["apple"])
        self.assertEquals(
            util.stringToList("[apple, banana]"),
            ["apple", "banana"])
        self.assertEquals(
            util.stringToList("[    apple   ,    banana  ]"),
            ["apple", "banana"])
        self.assertEquals(
            util.stringToList("apple, banana"), ["apple", "banana"])
        self.assertEquals(
            util.stringToList("apple;banana"), ["apple", "banana"])
        self.assertEquals(
            util.stringToList("apple banana"), ["apple", "banana"])
