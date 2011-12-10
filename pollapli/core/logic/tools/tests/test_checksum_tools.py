import os, logging, sys, shutil
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.logic.tools.checksum_tools import ChecksumTools

class Test_ChecksumTools(unittest.TestCase):    
    def setUp(self):
        self._testFileName = "TestFile.txt"
        self._write_mock_file(self._testFileName)

    def tearDown(self):
        os.remove(self._testFileName)
  
    @defer.inlineCallbacks
    def test_generate_hash(self):
        expChecksum = "18c0864b36d60f6036bf8eeab5c1fe7d"
        obsChecksum = yield ChecksumTools.generate_hash(filePath=self._testFileName)
        self.assertEquals(obsChecksum,expChecksum)
        
    @defer.inlineCallbacks
    def test_compare_hash(self):
        inputHash = "18c0864b36d60f6036bf8eeab5c1fe7d"
        obsCompare = yield ChecksumTools.compare_hash(inputHash, self._testFileName)
        self.assertTrue(obsCompare)
        
    @defer.inlineCallbacks
    def test_compare_hash_false(self):        
        inputHash = "12d0864b36d60f6036bf8eeab5c1feqsd"
        obsCompare = yield ChecksumTools.compare_hash(inputHash, self._testFileName)
        self.assertFalse(obsCompare)
            
    def _write_mock_file(self,path):
        f = open(path,"w") 
        f.write("somecontent")
        f.close()
    