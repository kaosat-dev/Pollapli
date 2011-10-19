import os
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from doboz_web.core.persistence.sqlite.device_sqlite_dao import DeviceSqliteDao
from doboz_web.core.logic.components.nodes.node import Device


class DeviceSqliteDaoTests(unittest.TestCase):    
    
    @defer.inlineCallbacks
    def setUp(self):
        self._dbpool = adbapi.ConnectionPool("sqlite3",'pollapli.db',check_same_thread=False)
        yield self._dbpool.runQuery('''CREATE TABLE devices(
             id INTEGER PRIMARY KEY,
             name TEXT,
             description TEXT,
             status TEXT NOT NULL DEFAULT "inactive"
             )''')
        self._deviceSqliteDao=DeviceSqliteDao(self._dbpool)
        
    @defer.inlineCallbacks
    def tearDown(self):
        yield self._dbpool.close()
        os.remove('pollapli.db')
    
    @defer.inlineCallbacks
    def test_save_device_new(self):
        input = Device(name="TestDevice",description="A test description")
        yield self._deviceSqliteDao.save_device(input)
        rows = yield self._dbpool.runQuery('''SELECT name,description,status FROM devices WHERE id =  1''')
        name,description,status = rows[0]
        exp = input
        obs = Device(name=name,description=description,status=status) 
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_save_device_existing(self):
        input = Device(name="TestDevice",description="A test description")
        yield self._deviceSqliteDao.save_device(input)
        input.name = "TestDeviceModified"
        yield self._deviceSqliteDao.save_device(input)
    
        result = yield self._dbpool.runQuery('''SELECT name,description,status FROM devices WHERE id =  1''')
        name,description,status = result[0]
        exp = input
        obs = Device(name=name,description=description,status=status) 
        self.assertEquals(obs,exp)

    @defer.inlineCallbacks
    def test_save_devices(self):
        input = [Device(name="TestDevice",description="A test description",status="inactive"),
                 Device(name="TestDevice",description="A test description",status="active")
        ]
        
        yield self._deviceSqliteDao.save_devices(input)
        
        expLDevices=input
        obsLDevices=[]
        rows = yield self._dbpool.runQuery('''SELECT name,description,status FROM devices''')
        for row in rows:
            name, description, status = row
            obsLDevices.append(Device(name=name,description=description,status=status))
            
        self.assertEquals(expLDevices,obsLDevices)

    @defer.inlineCallbacks
    def test_load_devicebyid(self): 
        yield self._insert_mockdevice()
        obs = yield self._deviceSqliteDao.load_device(id = 1)
        exp = Device(name = "TestDevice",description = "A test description load",status = "active")
        self.assertEquals(obs,exp)
        
    
#    def test_load_devicebyid2(self): 
#        self._insert_mockdevice()
#        d = self._deviceSqliteDao.load_device(id = 1)
#        
#        def _test_load_devicebyid(obs):
#              exp = Device(name = "TestDevice",description = "A test description load",status = "active")
#              self.assertEquals(obs,exp)
#              
#        d.addCallback(_test_load_devicebyid)
#        return d

    @defer.inlineCallbacks
    def test_load_multiple_devices(self):
        yield self._insert_multiple_mockdevices()
        exp = [Device(name="TestDeviceOne",description="A test description",status="inactive"),Device(name="TestDeviceTwo",description="Another test description",status="active")]
        obs =  yield self._deviceSqliteDao.load_devices()
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks 
    def _insert_mockdevice(self):
        yield self._dbpool.runQuery('''
        INSERT into devices VALUES(null,"TestDevice","A test description load","active")''')
        defer.returnValue(None)
        
    @defer.inlineCallbacks
    def _insert_multiple_mockdevices(self):
        yield self._dbpool.runQuery('''
        INSERT into devices VALUES(null,"TestDeviceOne","A test description","inactive")''')
        yield self._dbpool.runQuery('''
        INSERT into devices VALUES(null,"TestDeviceTwo","Another test description","active")''')

        