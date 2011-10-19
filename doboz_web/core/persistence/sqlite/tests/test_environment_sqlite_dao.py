import os
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from doboz_web.core.persistence.sqlite.environment_sqlite_dao import EnvironmentSqliteDao
from doboz_web.core.logic.components.environments.environment import Environment2


class EnvironmentSqliteDaoTests(unittest.TestCase):
    
    @defer.inlineCallbacks
    def setUp(self):
        self._dbpool = adbapi.ConnectionPool("sqlite3",'pollapli.db',check_same_thread=False)
        yield self._dbpool.runQuery('''CREATE TABLE environments(
             id INTEGER PRIMARY KEY,
             name TEXT,
             description TEXT,
             status TEXT NOT NULL DEFAULT "Live"
             )''')
        self._environmentSqliteDao=EnvironmentSqliteDao(self._dbpool)
        
    @defer.inlineCallbacks
    def tearDown(self):
        yield self._dbpool.close()
        os.remove('pollapli.db')
    
    @defer.inlineCallbacks
    def test_save_environment_new(self):
        input = Environment2(name="TestEnvironment",description="A description")
        exp=input
        yield self._environmentSqliteDao.save_environment(input)
        result = yield self._dbpool.runQuery('''SELECT name,description,status FROM environments WHERE id =  1''')
        name,description,status = result[0]
        obs = Environment2(name=name,description=description,status=status)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_save_environment_existing(self):
        input = Environment2(name="TestEnvironment",description="A description")
        yield self._environmentSqliteDao.save_environment(input)
        input.name="TestEnvironmentChanged"
        yield self._environmentSqliteDao.save_environment(input)
        
        result = yield self._dbpool.runQuery('''SELECT name,description,status FROM environments WHERE id =  1''')
        name,description,status = result[0]
        exp=input
        obs = Environment2(name=name,description=description,status=status)
        self.assertEquals(obs,exp)
     
    @defer.inlineCallbacks
    def test_load_environmentbyid(self):    
        yield self._insert_mockenv()
        input = Environment2(name="TestEnvironment",description="A test description",status="frozen")
        exp = input
        obs =  yield self._environmentSqliteDao.load_environment(id = 1)
        self.assertEquals(obs,exp)
    
    @defer.inlineCallbacks
    def test_load_all_environments(self):
        yield self._insert_multiple_mockenvs()
        exp = [Environment2(name="TestEnvironmentOne",description="A test description",status="frozen"),Environment2(name="TestEnvironmentTwo",description="Another test description",status="live")]
        obs = yield self._environmentSqliteDao.load_environments()
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks 
    def _insert_mockenv(self):
        yield self._dbpool.runQuery('''
        INSERT into environments VALUES(null,"TestEnvironment","A test description","frozen")''')
    
    @defer.inlineCallbacks 
    def _insert_multiple_mockenvs(self):
        yield self._dbpool.runQuery('''
        INSERT into environments VALUES(null,"TestEnvironmentOne","A test description","frozen")''')
        yield self._dbpool.runQuery('''
        INSERT into environments VALUES(null,"TestEnvironmentTwo","Another test description","live")''')
        defer.returnValue(None)