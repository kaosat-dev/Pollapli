import os
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from doboz_web.core.persistence.sqlite.sqlite_dao_manager import SqliteDaoManager
from doboz_web.core.logic.components.nodes.node import Device
from doboz_web.core.logic.components.updates.update_manager import Update2
from doboz_web.core.logic.components.environments.environment import Environment2




class SqliteDaoManagerTest(unittest.TestCase):    
    
    
    def setUp(self):
        self._sqliteDaoManager=SqliteDaoManager()
        
#    @defer.inlineCallbacks
#    def tearDown(self):
#        yield self._dbpool.close()
#        os.remove('pollapli.db')
    
    def test_load_device(self):
        input = Device(name="testDevice",description = "just a device")
        yield self._sqliteDaoManager.save_device(input)
        exp = input 
        obs = self._sqliteDaoManager.load_device(id = 1)