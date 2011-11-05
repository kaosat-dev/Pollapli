import os
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from pollapli.core.persistence.sqlite.device_sqlite_dao import DeviceSqliteDao
from pollapli.core.logic.components.nodes.node import Device


class DeviceSqliteDaoTests(unittest.TestCase):    
    
    def setUp(self):
        self._dbpool = adbapi.ConnectionPool("sqlite3",'pollapli.db',check_same_thread=False)
        self._deviceSqliteDao=DeviceSqliteDao(self._dbpool)        
        
    @defer.inlineCallbacks
    def tearDown(self):
        yield self._dbpool.close()
        os.remove('pollapli.db')
    
    @defer.inlineCallbacks
    def test_save_device_new(self):
        input = Device(name="TestDevice",description="A test description")
        yield self._deviceSqliteDao.save_device(input)
        
        exp = input
        obs = yield self._deviceSqliteDao.load_device(id = 1) 
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_save_device_existing(self):
        input = Device(name="TestDevice",description="A test description")
        yield self._deviceSqliteDao.save_device(input)
        input.name = "TestDeviceModified"
        yield self._deviceSqliteDao.save_device(input)
    
        exp = input
        obs = yield self._deviceSqliteDao.load_device(id = 1)
        self.assertEquals(obs,exp)

    @defer.inlineCallbacks
    def test_save_devices(self):
        input = [Device(name="TestDevice",description="A test description",status="inactive"),
                 Device(name="TestDevice",description="A test description",status="active")]        
        yield self._deviceSqliteDao.save_devices(input)
        expLDevices = input 
        obsLDevices = yield self._deviceSqliteDao.load_devices()

        self.assertEquals(expLDevices,obsLDevices)

    @defer.inlineCallbacks
    def test_load_devicebyid(self): 
        input = Device(name = "TestDevice",description = "A test description load",status = "active")
        yield self._deviceSqliteDao.save_device(input)
        
        exp = input
        obs = yield self._deviceSqliteDao.load_device(id = 1)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_load_multiple_devices(self):
        input = [Device(name="TestDeviceOne",description="A test description",status="inactive"),Device(name="TestDeviceTwo",description="Another test description",status="active")]
        yield self._deviceSqliteDao.save_devices(input)
        exp = input 
        obs =  yield self._deviceSqliteDao.load_devices()
        self.assertEquals(obs,exp)
        