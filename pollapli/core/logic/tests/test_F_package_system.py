import os, logging, sys, shutil, SimpleHTTPServer, SocketServer,Thread
from zipfile import ZipFile
from SimpleHTTPServer import SimpleHTTPRequestHandler
from twisted.trial import unittest
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.logic.components.packages.package import Package
from pollapli.core.persistence.persistence_layer import PersistenceLayer
from pollapli.core.logic.components.packages.package_manager import PackageManager
from pollapli.core.logic.tools.path_manager import PathManager

class PackageSystemTest(unittest.TestCase):   
    @defer.inlineCallbacks 
    def setUp(self):
        self._pathManager = PathManager()
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
        if not os.path.exists("addons"):
            os.makedirs("addons")
            
        self._pathManager.addOnPath = "addons"
        self._pathManager.tmpPath = "tmp"
        
        self._persistenceLayer = PersistenceLayer()
        self._packageManager = PackageManager(self._persistenceLayer,self._pathManager)
        yield self._packageManager.setup()
       
    @defer.inlineCallbacks  
    def tearDown(self):
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")
        if os.path.exists("addons"):
            shutil.rmtree("addons")

        yield self._persistenceLayer.tearDown()
        if os.path.exists("pollapli.db"):
            os.remove("pollapli.db")
        self._stop_mock_file_server()

    def test_refresh_packageList(self):
        package1 = Package()
        package2 = Package()
        exp = [package1, package2]
        obs = self._packageManager._packages
        self.assertEquals(obs,exp)    
    
    
    @defer.inlineCallbacks
    def test_setup_package(self):
        """Test for downloading and installing a package"""
        fileServePath = "fileserve"
        os.makedirs(fileServePath)
        self._write_mock_compressedPackage("TestAddOn", fileServePath)
        self._start_mock_file_server(fileServePath)
        
        addOn = Package(type = "addon", name = "TestAddOn", version = "0.0.1",file="TestAddOn.zip")
        addOn.downloadUrl = "http://localhost:8765/TestAddOn.zip"
        self._packageManager._availablePackages[addOn._id] = addOn
        yield self._packageManager._download_package(id = addOn._id)
        
        if os.path.exists(fileServePath):
            shutil.rmtree(fileServePath)
        packagePath = os.path.join(self._pathManager.tmpPath,addOn.file)    
        self.assertTrue(os.path.exists(packagePath))  
        
    def test_package_reloading(self):
        pass 
        
    def _start_mock_file_server(self,fileServePath):
        self._handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self.httpd = SocketServer.TCPServer(("", self._mockServerport), self._handler)
        print ("serving on port %i" %self._mockServerport)
        self._t=Thread(target=self.httpd.serve_forever).start()    
            
    def _stop_mock_file_server(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        print ("stopped serving on port %i" %self._mockServerport)  
        
    def _write_mock_packageFile(self,path):
        f = open(path,"w") 
        f.write("somecontent")
        f.close()
        
    def _write_mock_compressedPackage(self,name,path):
        packagePath = os.path.join(path,name)
        os.makedirs(packagePath)
        addOnFileOnePath = os.path.join(packagePath,"addOnFileOne.py")
        addOnFileTwoPath = os.path.join(packagePath,"addOnFileTwo.py")
        addOnPkgInfoFileName = "PKG-INFO" 
        #self._write_mock_pkgInfo(addOnPkgInfoFileName)
        
        self._write_mock_packageFile(addOnFileOnePath)
        self._write_mock_packageFile(addOnFileTwoPath)
    
        packageFile = ZipFile(packagePath+".zip", 'w')
        packageFile.write(addOnFileOnePath,os.path.join(name,"addOnFileOne.py"))
        packageFile.write(addOnFileTwoPath,os.path.join(name,"addOnFileTwo.py"))
        packageFile.close()
        shutil.rmtree(packagePath)
        
    def _write_mock_compressedPackage2(self,rootName,path,zipFileName):
        packagePath = os.path.join(path,rootName)
        os.makedirs(packagePath)
        addOnFileOnePath = os.path.join(packagePath,"addOnFileOne.py")
        addOnFileTwoPath = os.path.join(packagePath,"addOnFileTwo.py")
        addOnFileThreePath = os.path.join(packagePath,"addOnFileThree.py")
        addOnFileFourPath = os.path.join(packagePath,"addOnFileFour.py")
        addOnPkgInfoFileName = "PKG-INFO" 
        #self._write_mock_pkgInfo(addOnPkgInfoFileName)
        
        self._write_mock_packageFile(addOnFileOnePath)
        self._write_mock_packageFile(addOnFileTwoPath)
        self._write_mock_packageFile(addOnFileThreePath)
        self._write_mock_packageFile(addOnFileFourPath)
        packageFile = ZipFile(os.path.join(path,zipFileName+".zip"), 'w')
        packageFile.write(addOnFileOnePath,os.path.join(rootName,"addOnFileOne.py"))
        packageFile.write(addOnFileTwoPath,os.path.join(rootName,"addOnFileTwo.py"))
        packageFile.write(addOnFileTwoPath,os.path.join(rootName,"addOnFileThree.py"))
        packageFile.write(addOnFileFourPath,os.path.join(rootName,"subdir/addOnFileFour.py"))
        packageFile.close()
        shutil.rmtree(packagePath)
       
        
    def _write_mock_pkgInfo(self,path):
        os.makedirs("EGG-INFO")
        f = open(os.path.join(path,"EGG-INFO","PKG-INFO"),"w")
        f.write("Metadata-Version: 1.0\n")
        f.write("Name: Example AddOn\n")
        f.write("Version: 0.0.1\n")
        f.write("Summary: a simple addOn test\n")
        f.write("Home-page: http://github.com/kaosat-dev/Pollapli\n")
        f.write("Author: Mark 'ckaos' Moissette\n")
        f.write("Author-email: kaosat.dev@gmail.com\n")
        f.write("License: GPL\n")
        f.write("Description: UNKNOWN\n")
        f.write("Keywords: web remote control remote monitoring reprap repstrap\n")
        f.write("Platform: UNKNOWN\n")
        f.write("Classifier: Development Status :: 1 - Planning\n")
        f.write("Classifier: Topic :: Utilities\n")
        f.write("Classifier: Natural Language :: English\n")
        f.write("Classifier: Operating System :: OS Independent\n")
        f.write("Classifier: Programming Language :: Python :: 2.6\n")
        f.close()

        
    def _write_mock_packageListFile(self, packageListPath):
         
        f = open(packageListPath,"w")
        f.write('''{
            "packages": [
            {
                "id": "23b0d813-a6b2-461a-88ad-a7020ae66742",
                "type": "addon",
                "name": "Test AddOn",
                "version": "0.0.1",
                "description": "A test Add on",
                "tags": [
                        "test",
                        "something"
                        ],
                "img": "testAddon.png",
                "file": "testAddon-0.0.1.egg",
                "fileHash": "80e157c0f10baef206ee2de03fae7449",
                "downloadUrl" : "http://kaosat.net/pollapli/testAddon-0.0.1.egg"
            },
            {
                "id": "23b0d813-a6b2-461a-88ad-a7020ae64542",
                "type": "update",
                "name": "Test Update",
                "target": "pollapli",
                "targetId": "23b0d813-a6b2-461a-88ad-a7020ae67742",
                "fromVersion" : "0.5.0",
                "toVersion" : "0.6.0",
                "description": "A test Update",
                "tags": [
                        "update",
                        "fish"
                        ],
                "img": "testPackage.png",
                "file": "testPackage-0.2.1.egg",
                "fileHash": "80e157c0f10baef206ee2de03fae7449",
                "downloadUrl" : "http://kaosat.net/pollapli/testUpdate-0.2.1.egg"
            }]}''')
        f.close()



    