import os
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from doboz_web.core.persistence.sqlite.environment_sqlite_dao import EnvironmentSqliteDao
from doboz_web.core.logic.components.environments.environment import Environment2


class EnvironmentSqliteDaoTests(unittest.TestCase):
    
    def setUp(self):
        self._dbpool = adbapi.ConnectionPool("sqlite3",'pollapli.db',check_same_thread=False)
        self._environmentSqliteDao=EnvironmentSqliteDao(self._dbpool)
        
    @defer.inlineCallbacks
    def tearDown(self):
        yield self._dbpool.close()
        os.remove('pollapli.db')
    
    @defer.inlineCallbacks
    def test_save_environment_new(self):
        input = Environment2(name="TestEnvironment",description="A description")
        yield self._environmentSqliteDao.save_environment(input)
        
        exp=input
        obs = yield self._environmentSqliteDao.load_environment(id = 1)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_save_environment_existing(self):
        input = Environment2(name="TestEnvironment",description="A description")
        yield self._environmentSqliteDao.save_environment(input)
        input.name="TestEnvironmentChanged"
        yield self._environmentSqliteDao.save_environment(input)
        
        exp=input
        obs = yield self._environmentSqliteDao.load_environment(id = 1)
        self.assertEquals(obs,exp)
     
    @defer.inlineCallbacks
    def test_load_environmentbyid(self):  
        input = Environment2(name="TestEnvironment",description="A test description",status="frozen")
        yield self._environmentSqliteDao.save_environment(input)
        exp = input
        obs =  yield self._environmentSqliteDao.load_environment(id = 1)
        self.assertEquals(obs,exp)
    
    @defer.inlineCallbacks
    def test_load_all_environments(self):
        input = [Environment2(name="TestEnvironmentOne",description="A test description",status="frozen"),Environment2(name="TestEnvironmentTwo",description="Another test description",status="live")]
        yield self._environmentSqliteDao.save_environments(input)
        exp = input
        obs = yield self._environmentSqliteDao.load_environments()
        self.assertEquals(obs,exp)
        