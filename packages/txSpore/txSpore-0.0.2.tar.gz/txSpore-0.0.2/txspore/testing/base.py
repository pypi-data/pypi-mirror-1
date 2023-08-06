from twisted.python import log
from twisted.python.filepath import FilePath
from twisted.trial.unittest import TestCase


class TXSporeTestCase(TestCase):

    def setUp(self):
        # setup logging
        self.catcher = []
        self.observer = self.catcher.append
        log.addObserver(self.observer)
        self.addCleanup(log.removeObserver, self.observer)

        # setup convenient tempfile objects
        self.tempFile = self.mktemp()
        self.tempFilePath = FilePath(self.tempFile)
        self.tempDirname = self.tempFilePath.dirname()
        self.tempBasename = self.tempFilePath.basename()
