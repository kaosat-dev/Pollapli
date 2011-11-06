import os, logging, sys,shutil
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.logic.logic_layer import LogicLayer
from pollapli.core.logic.components.updates.update import Update
from pollapli.core.persistence.persistence_layer import PersistenceLayer
from pollapli.core.logic.components.updates.update_manager import UpdateManager
from pollapli.core.logic.tools.path_manager import PathManager


class UpdateSystemTest(unittest.TestCase):   
    @defer.inlineCallbacks 
    def setUp(self):
        self._pathManager = PathManager()
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
        self._pathManager.tmpPath = "tmp"
        
        self._persistenceLayer = PersistenceLayer()
        self._updateManager = UpdateManager(self._persistenceLayer,self._pathManager)
        yield self._updateManager.setup()
       
    @defer.inlineCallbacks  
    def tearDown(self):
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")
        yield self._persistenceLayer.tearDown()
        if os.path.exists("pollapli.db"):
            os.remove("pollapli.db")
        
    def test_fetch_updateList(self):
        update1 = Update()
        update2 = Update()
        exp = [update1, update2]
        obs = self._updateManager._updates
        self.assertEquals(obs,exp)    
    
    def test_parse_updateListFile(self):
        updateListPath = os.path.join(self._pathManager.tmpPath,"pollapli_updates.json")
        self._write_mock_updateListFile(updateListPath)
        
        update1 = Update(type = "addon", name = "TestAddOn", version = "0.0.1")      
        update2 = Update(type = "update", name = "TestUpdate", version = "0.2.1")
        
        lExpUpdates = [update1, update2]
        self._updateManager._parse_update_file()
        lObsUpdates = self._updateManager._updates.values()
        
        self.assertEquals(lObsUpdates, lExpUpdates)
        os.remove(updateListPath)
        
    def test_setup_update(self):
        updatePath = "update"
        self.assertTrue(os.path.exists(updatePath))
        
        
    def test_recall_updateManager(self):
        updatePath = "update"
        self.assertTrue(os.path.exists(updatePath))
        
    def _write_mock_updateListFile(self, updateListPath):
         
        f = open(updateListPath,"w")
        f.write('''{
            "updates": [
            {
                "id": "23b0d813-a6b2-461a-88ad-a7020ae66742",
                "type": "addon",
                "name": "TestAddOn",
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
                "name": "TestUpdate",
                "version": "0.2.1",
                "description": "A test Update",
                "tags": [
                        "update",
                        "fish"
                        ],
                "img": "testUpdate.png",
                "file": "testUpdate-0.2.1.egg",
                "fileHash": "80e157c0f10baef206ee2de03fae7449",
                "downloadUrl" : "http://kaosat.net/pollapli/testUpdate-0.2.1.egg"
            }]}''')
        f.close()