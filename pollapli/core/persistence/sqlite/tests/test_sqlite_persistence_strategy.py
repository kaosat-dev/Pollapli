import os
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from pollapli.core.persistence.sqlite.sqlite_persistence_strategy import SqlitePersistenceStrategy
from pollapli.core.logic.components.nodes.node import Device
from pollapli.core.logic.components.environments.environment import Environment2
from pollapli.core.logic.components.updates.update_manager import Update2


class SqlitePersistanceStrategyTests(unittest.TestCase):    
    
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    @defer.inlineCallbacks
    def test_get_store_db_creation(self):      
        env = Environment2(name = "environmentOne")
        update = Update2(type = "update", name = "updateOne")
        
        expEnvironmentDbName = "environmentOne.db"
        expUpdateDbName = "pollapli.db"
             
        strategy = SqlitePersistenceStrategy()  
        obsEnvironmentDbPool = strategy.get_store(env,"Environment2")
        obsUpdateDbPool = strategy.get_store(update,"Update")
      
        try:
            yield obsUpdateDbPool.runQuery('''select * from devices''')
        except:pass 
        try:
            yield obsEnvironmentDbPool.runQuery('''select * from devices''')
        except:pass 
      
        self.assertTrue(os.path.exists(expUpdateDbName))
        self.assertTrue(os.path.exists(expEnvironmentDbName))

        yield strategy.tear_down()
        os.remove(expEnvironmentDbName)
        os.remove(expUpdateDbName)

    @defer.inlineCallbacks
    def test_get_store_multiple_dynamic_db_creation(self):
        expEnvironmentOneDbName = "environmentOne.db"
        expEnvironmentTwoDbName = "environmentTwo.db"  
        
        envOne = Environment2(name = "environmentOne")
        envTwo = Environment2(name = "environmentTwo")
        
        strategy = SqlitePersistenceStrategy()  
        environmentOneDbPool = strategy.get_store(envOne,"Environment2")
        environmentTwoDbPool = strategy.get_store(envTwo,"Environment2")
        
        try:
            yield environmentOneDbPool.runQuery('''select * from devices''')
        except:pass 
        try:
            yield environmentTwoDbPool.runQuery('''select * from devices''')
        except:pass 
        
        self.assertTrue(os.path.exists(expEnvironmentOneDbName))
        self.assertTrue(os.path.exists(expEnvironmentTwoDbName))
        
        yield strategy.tear_down()
        os.remove(expEnvironmentOneDbName)
        os.remove(expEnvironmentTwoDbName)
    
    @defer.inlineCallbacks
    def test_get_store_correct_db_from_sub_elements(self):
        expEnvironmentOneDbName = "environmentOne.db"
        env = Environment2(name = "environmentOne")
        device = Device(name = "arduino")
        device. _parent = env
      
        strategy = SqlitePersistenceStrategy()  
        deviceDbPool = strategy.get_store(device,"Device")
        
        try:
            yield deviceDbPool.runQuery('''select * from devices''')
        except:pass 
        
        self.assertTrue(os.path.exists(expEnvironmentOneDbName))
        
        yield strategy.tear_down()
        os.remove(expEnvironmentOneDbName)
      