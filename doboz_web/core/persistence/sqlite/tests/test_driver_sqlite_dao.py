import os
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from doboz_web.core.persistence.sqlite.driver_sqlite_dao import DriverSqliteDao
from doboz_web.core.logic.components.drivers.driver import Driver


class DriverSqliteDaoTests(unittest.TestCase):    
    
    @defer.inlineCallbacks
    def setUp(self):
        self._dbpool = adbapi.ConnectionPool("sqlite3",'pollapli.db',check_same_thread=False)
        yield self._dbpool.runQuery('''CREATE TABLE drivers(
             id INTEGER PRIMARY KEY,
             name TEXT,
             description TEXT,
             status TEXT NOT NULL DEFAULT "inactive"
             )''')
        self._driverSqliteDao=DriverSqliteDao(self._dbpool)
        
    @defer.inlineCallbacks
    def tearDown(self):
        yield self._dbpool.close()
        os.remove('pollapli.db')
    
    @defer.inlineCallbacks
    def test_save_node_new(self):
        input = Driver2(name="TestDriver",description="A test description")
        yield self._driverSqliteDao.save_driver(input)
        rows = yield self._dbpool.runQuery('''SELECT name,description,status FROM drivers WHERE id =  1''')
        name,description,status = rows[0]
        exp = input
        obs = Driver2(name=name,description=description,status=status) 
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_save_node_existing(self):
        input = Driver2(name="TestDriver",description="A test description")
        yield self._driverSqliteDao.save_driver(input)
        input.name = "TestDriverModified"
        yield self._driverSqliteDao.save_driver(input)
    
        result = yield self._dbpool.runQuery('''SELECT name,description,status FROM drivers WHERE id =  1''')
        name,description,status = result[0]
        exp = input
        obs = Driver2(name=name,description=description,status=status) 
        self.assertEquals(obs,exp)

    @defer.inlineCallbacks
    def test_save_drivers(self):
        input = [Driver2(name="TestDriver",description="A test description",status="inactive"),
                 Driver2(name="TestDriver",description="A test description",status="active")
        ]
        
        yield self._driverSqliteDao.save_drivers(input)
        
        expLDrivers=input
        obsLDrivers=[]
        rows = yield self._dbpool.runQuery('''SELECT name,description,status FROM drivers''')
        for row in rows:
            name, description, status = row
            obsLDrivers.append(Driver2(name=name,description=description,status=status))
            
        self.assertEquals(expLDrivers,obsLDrivers)

    @defer.inlineCallbacks
    def test_load_nodebyid(self): 
        yield self._insert_mocknode()
        obs = yield self._driverSqliteDao.load_driver(id = 1)
        exp = Driver2(name = "TestDriver",description = "A test description load",status = "active")
        self.assertEquals(obs,exp)
        

    @defer.inlineCallbacks
    def test_load_multiple_drivers(self):
        yield self._insert_multiple_mockdrivers()
        exp = [Driver2(name="TestDriverOne",description="A test description",status="inactive"),Driver2(name="TestDriverTwo",description="Another test description",status="active")]
        obs =  yield self._driverSqliteDao.load_drivers()
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks 
    def _insert_mocknode(self):
        yield self._dbpool.runQuery('''
        INSERT into drivers VALUES(null,"TestDriver","A test description load","active")''')
        defer.returnValue(None)
        
    @defer.inlineCallbacks
    def _insert_multiple_mockdrivers(self):
        yield self._dbpool.runQuery('''
        INSERT into drivers VALUES(null,"TestDriverOne","A test description","inactive")''')
        yield self._dbpool.runQuery('''
        INSERT into drivers VALUES(null,"TestDriverTwo","Another test description","active")''')

        