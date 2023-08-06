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

    def test_parseAtomDate(self):
        date = "2009-09-11T02:15:46.557Z"
        datetime = util.parseAtomDate(date)
        self.assertEquals(datetime.strftime("%Y-%m-%dT%T"), date.split(".")[0])

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


    def test_scrubXMLNameSpace(self):
        originalTag = "{http://www.w3.org/2005/Atom}id"
        tag = util.scrubXMLNameSpace(originalTag)
        self.assertEquals(tag, "id")


    def test_validateParametersWithValidParameter(self):
        legalValues = ["a", "b", "c"]
        check = util.validateParameters("a", legalValues)
        self.assertEquals(check, "a")


    def test_validateParametersWithEmptyParameter(self):
        legalValues = ["a", "b", "c", ""]
        check = util.validateParameters("", legalValues)
        self.assertEquals(check, "")


    def test_validateParametersWithInvalidParameter(self):
        legalValues = ["a", "b", "c"]
        self.assertRaises(ValueError, util.validateParameters, 
                          "d", legalValues)
        try:
            util.validateParameters("d", legalValues)
        except ValueError, error:
            self.assertEquals(error.message, "'d' is not one of 'a', 'b', 'c'")
