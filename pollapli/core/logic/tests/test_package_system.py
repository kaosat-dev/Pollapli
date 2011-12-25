import os, logging, sys, shutil, SimpleHTTPServer, SocketServer
from zipfile import ZipFile
from twisted.trial import unittest
from zope.interface import Interface,classProvides 
from twisted.plugin import IPlugin
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.logic.components.packages.package import Package
from pollapli.core.logic.components.packages.package_manager import PackageManager
from pollapli.core.logic.tools.path_manager import PathManager

#TODO: fix all the package testing tests , since all files and folder should be moved to a main folder
class TestPackageSystem(unittest.TestCase):   
    
    def setUp(self):
        self._path_manager = PathManager()
        self._packageManager = PackageManager(pathManager=self._path_manager)
        self._path_manager._addon_path = os.path.abspath("addons")
        self._path_manager.tmpPath = os.path.abspath("tmp")

        if not os.path.exists(self._path_manager.tmpPath):
            os.makedirs(self._path_manager.tmpPath)
        if not os.path.exists(self._path_manager._addon_path):
            os.makedirs(self._path_manager._addon_path)
       # yield self._packageManager.setup()
       
    def tearDown(self):
        if os.path.exists(self._path_manager.tmpPath):
            shutil.rmtree(self._path_manager.tmpPath)
        if os.path.exists(self._path_manager._addon_path):
            shutil.rmtree(self._path_manager._addon_path)
                
    def test_parse_packageListFile(self):
        packageListPath = os.path.join(self._path_manager.tmpPath,"pollapli_packages.json")
        self._write_mock_packageListFile(packageListPath)
        
        package1 = Package(type = "addon", name = "Test AddOn", version = "0.0.1")      
        package2 = Package(type = "update", name = "Test Update", targetId="23b0d813-a6b2-461a-88ad-a7020ae67742", fromVersion="0.5.0", toVersion="0.6.0")
        
        lExpPackages = [package1, package2]
        self._packageManager._parse_packageListFile()
        lObsPackages = self._packageManager._available_packages.values()
        
        self.assertEquals(lObsPackages[0],lExpPackages[0])
        self.assertEquals(lObsPackages, lExpPackages)
        os.remove(packageListPath)
        
    @defer.inlineCallbacks
    def test_install_addon(self):
        self._write_mock_compressedPackage("TestAddOn", self._path_manager.tmpPath)
        addOn = Package(type = "addon", name = "TestAddOn", version = "0.0.1",file="TestAddOn.zip")
        addOn.downloaded = True
        
        self._packageManager._available_packages[addOn.cid] = addOn
        yield self._packageManager.install_package(id = addOn.cid)

        packagePath = os.path.join(self._path_manager._addon_path,"TestAddOn")    
        self.assertTrue(os.path.exists(packagePath))
        self.assertTrue(self._packageManager._installed_packages[addOn.cid],addOn)
        
    @defer.inlineCallbacks
    def test_install_addon_update(self):
        self._write_mock_compressedPackage("TestAddOn", self._path_manager.tmpPath)
        addOn = Package(type = "addon", name = "TestAddOn", version = "0.0.1",file="TestAddOn.zip")
        addOn.downloaded = True    
        self._packageManager._available_packages[addOn.cid] = addOn
        yield self._packageManager.install_package(id = addOn.cid)
        
        self._write_mock_compressedPackage2("TestAddOn", self._path_manager.tmpPath,"TestUpdate")
        update = Package(type = "update", name = "TestUpdate", fromVersion= "0.0.1", toVersion = "0.0.2", file="TestUpdate.zip")
        update.targetId = addOn.cid
        update.downloaded = True 
        self._packageManager._available_packages[update.cid] = update
        yield self._packageManager.install_package(id = update.cid)

        self.assertEquals(self._packageManager._installed_packages[addOn.cid].version , update.toVersion)
        expNewFileOne = os.path.join(self._path_manager._addon_path,"TestAddOn","addOnFileThree.py")
        expNewFileTwo = os.path.join(self._path_manager._addon_path,"TestAddOn","subdir","addOnFileFour.py")
        self.assertTrue(os.path.exists(expNewFileOne))
        self.assertTrue(os.path.exists(expNewFileTwo))
        
    def test_enable_addon(self):
        addOn = Package(type = "addon", name = "TestAddOn")
        self._packageManager._installed_packages[addOn.cid] = addOn
        self._packageManager.enable_addon(addOn.cid)
        
        self.assertTrue(self._packageManager.get_package(addOn.cid).enabled)
         
    def test_disable_addon(self):
        addOn = Package(type = "addon", name = "TestAddOn")
        self._packageManager._installed_packages[addOn.cid] = addOn
        self._packageManager.disable_addon(addOn.cid)
        
        self.assertFalse(self._packageManager.get_package(addOn.cid).enabled)
        
    @defer.inlineCallbacks
    def test_get_plugins(self):
        addOn = Package(type = "addon", name = "TestAddOn", version = "0.0.1",file="TestAddOn.zip")
        addOn.downloaded = True    
        self._packageManager._available_packages[addOn.cid] = addOn
        
        self._write_mock_compressedPackageWithMockPlugin("TestAddOn", self._path_manager.tmpPath,"TestAddOn")
        yield self._packageManager.install_package(id = addOn.cid)
        
        expLPlugins = [plugin.__name__ for plugin in [IMockPluginImplementation,IMockPluginImplementationToo]]
        obsLPlugins = [plugin.__name__ for plugin in (yield self._packageManager.get_plugins(IMockPlugin))]

        self.assertEquals(obsLPlugins,expLPlugins)
    
    def test_save_installedPackageList(self):
        pass
    def test_load_installedPackageList(self):
        pass
    
    def _write_mock_packageFile(self,path):
        f = open(path,"w") 
        f.write("somecontent")
        f.close()
        
    def _write_mock_file(self,path="",content=""):
        f = open(path,"w") 
        f.write(content)
        f.close()
        
    def _write_mock_pluginFile(self,path):
        f = open(path,"w") 
        f.write("from zope.interface import Interface,classProvides\n")
        f.write("from twisted.plugin import IPlugin\n")
        f.write("from pollapli.core.logic.tests.test_package_system import IMockPlugin\n")
        f.write("class IMockPluginImplementation(object):\n")
        f.write("\tclassProvides(IPlugin, IMockPlugin)\n")
        f.write("\tdef __init__(self,*args,**kwargs):\n")
        f.write("\t\tpass\n")
        f.write("def __eq__(self, other):\n")
        f.write("\treturn self.__class__.__name__ == other.__class__.__name__\n")
        f.close()
        
    def _write_mock_otherPluginFile(self,path):
        f = open(path,"w") 
        f.write("from zope.interface import Interface,classProvides\n")
        f.write("from twisted.plugin import IPlugin\n")
        f.write("from pollapli.core.logic.tests.test_package_system import IMockPlugin\n")        
        f.write("class IMockPluginImplementationToo(object):\n")
        f.write("\tclassProvides(IPlugin, IMockPlugin)\n")
        f.write("\tdef __init__(self,*args,**kwargs):\n")
        f.write("\t\tpass\n")
        f.write("def __eq__(self, other):\n")
        f.write("\treturn self.__class__.__name__ == other.__class__.__name__\n")
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
        
    def _write_mock_compressedPackageWithMockPlugin(self,rootName,path,zipFileName):
        packagePath = os.path.join(path,rootName)
        os.makedirs(packagePath)
        addOnFileOnePath = os.path.join(packagePath,"addOnFileOne.py")
        addOnFileTwoPath = os.path.join(packagePath,"addOnFileTwo.py")
        mainInitPath = os.path.join(packagePath,"__init__.py")
        
        self._write_mock_file(mainInitPath)
        self._write_mock_pluginFile(addOnFileOnePath)
        self._write_mock_otherPluginFile(addOnFileTwoPath)
        
        packageFile = ZipFile(os.path.join(path,zipFileName+".zip"), 'w')
        packageFile.write(mainInitPath, os.path.join(rootName,rootName,"__init__.py"))
        packageFile.write(addOnFileOnePath, os.path.join(rootName,rootName,"addOnFileOne.py"))
        packageFile.write(mainInitPath, os.path.join(rootName,rootName,"subdir/__init__.py"))
        packageFile.write(addOnFileTwoPath, os.path.join(rootName,rootName,"subdir/addOnFileTwo.py"))
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
        f.write("Author-email: me@gmail.com\n")
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


class IMockPlugin(Interface):
    pass
class IMockPluginImplementation(object):
    classProvides(IPlugin, IMockPlugin)
    def __init__(self,*args,**kwargs):
        pass
    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__
    
class IMockPluginImplementationToo(object):
    classProvides(IPlugin, IMockPlugin)
    def __init__(self,*args,**kwargs):
        pass
    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__
