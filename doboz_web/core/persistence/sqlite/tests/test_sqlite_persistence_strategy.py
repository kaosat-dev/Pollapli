import os
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from doboz_web.core.persistence.sqlite.device_sqlite_dao import DeviceSqliteDao
from doboz_web.core.logic.components.nodes.node import Device


class SqlitePersistanceStrategyTests(unittest.TestCase):    
    
    def setUp(self):
        pass
        
    def tearDown(self):
      pass
    
    def test_get_store(self):  
        updateDbpoolName = "pollapli.db" 
        environmentOneDbpoolName = "environmentOne.db"
        environmentTwoDbpoolName = "environmentTwo.db"  
        deviceOneDbpoolName = "environmentOne.db"
        deviceTwoDbpoolName = "environmentTwo.db"
        
        exp = input
        obs = Device(name=name,description=description,status=status) 
        self.assertEquals(obs,exp)
        


 

        