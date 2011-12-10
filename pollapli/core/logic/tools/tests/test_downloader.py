import os, logging, sys, shutil, SimpleHTTPServer, SocketServer
from zipfile import ZipFile
from threading import Thread
from twisted.trial import unittest
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.logic.tools.path_manager import PathManager
from pollapli.core.logic.tools.downloader import DownloaderWithProgress

#TODO: solve mock file server serving directory problem
class DownloaderTest(unittest.TestCase):    
    def setUp(self):
        self._mockServerport = 8765
        self._fileServePath = ""
        self._testFileName = "TestFile.txt"
        self._downloadUrl = "http://localhost:%i/%s" %(self._mockServerport,self._testFileName)
        
        self._downloader = DownloaderWithProgress()
        self._pathManager = PathManager()
        self._pathManager.tmpPath = "tmp"
        if not os.path.exists("tmp"):
            os.makedirs("tmp")       
        try: 
            if not os.path.exists(self._fileServePath):
                os.makedirs(self._fileServePath)
        except:pass  
        
        self._start_mock_file_server(self._fileServePath)
        self._downloadPath = os.path.join(self._pathManager.tmpPath,self._testFileName)
        self._testFilePath = os.path.join(self._fileServePath,self._testFileName)
        self._write_mock_file(self._testFilePath)
        
    def tearDown(self):
        self._stop_mock_file_server()
        os.remove(self._testFileName)
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")
        if os.path.exists(self._fileServePath): 
            shutil.rmtree(self._fileServePath)
            
    @defer.inlineCallbacks
    def test_download_file(self):
        yield self._downloader.download(url = self._downloadUrl ,destination = self._downloadPath)
        expFilePath = self._downloadPath
        self.assertTrue(os.path.exists(expFilePath))
            
    @defer.inlineCallbacks
    def test_download_file_with_progress_update(self):
        obsUpdatableObject = MockUpdatableObject()
        expUpdatableObject = MockUpdatableObject(100)
        expFilePath = self._downloadPath
        
        yield self._downloader.download(url = self._downloadUrl ,destination = self._downloadPath, object = obsUpdatableObject)
        
        self.assertEquals(obsUpdatableObject,expUpdatableObject)
        self.assertTrue(os.path.exists(expFilePath))
        
    @defer.inlineCallbacks
    def test_download_file_with_checksum(self):
        obsUpdatableObject = MockUpdatableObject()
        expFilePath = self._downloadPath        
        yield self._downloader.download(url = self._downloadUrl ,destination = self._downloadPath, object = obsUpdatableObject, refChecksum = "18c0864b36d60f6036bf8eeab5c1fe7d")
        self.assertTrue(os.path.exists(expFilePath))
    
    def test_download_file_with_checksumError(self):
        obsUpdatableObject = MockUpdatableObject()
        d = self._downloader.download(url = self._downloadUrl ,destination = self._downloadPath, object = obsUpdatableObject, refChecksum = "18c0864b36d60f6036bf8eeab5c1fe7f")
        return self.assertFailure(d, Exception)
        
    def _start_mock_file_server(self,fileServePath):
        self._handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self.httpd = SocketServer.TCPServer(("", self._mockServerport), self._handler)
        print ("serving on port %i" %self._mockServerport)
        self._t=Thread(target=self.httpd.serve_forever).start()    
            
    def _stop_mock_file_server(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        print ("stopped serving on port %i" %self._mockServerport)
        
    def _write_mock_file(self,path):
        f = open(path,"w") 
        f.write("somecontent")
        f.close()
        
class MockUpdatableObject(object):
    def __init__(self, downloadProgress = 0):
        self.downloadProgress = downloadProgress
    def __eq__(self, other):
        return self.downloadProgress == other.downloadProgress