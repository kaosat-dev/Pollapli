from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from doboz_web.run import * 
from doboz_web.core.persistance.sqlite.environment_sqlite_dao import EnvironmentSqliteDao
from doboz_web.core.logic.components.environments.environment import Environment2
from twisted.python import log,failure

#TODO : replace mutual dependency of tests with manual sqlite inserts/selects

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
      
        self.environmentSqliteDao=EnvironmentSqliteDao(self._dbpool)
        
    @defer.inlineCallbacks
    def tearDown(self):
        yield self._dbpool.close()
        os.remove('pollapli.db')
    
    @defer.inlineCallbacks
    def test_save_environment(self):
        input = Environment2(name="test",description="test")
        exp=input
        yield self.environmentSqliteDao.save_environment(input)
        result = yield self._dbpool.runQuery('''SELECT name,description,status FROM environments WHERE id =  1''')
        name,description,status = result[0]
        obs = Environment2(name=name,description=description,status=status)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks 
    def test_load_environmentbyid(self):    
        yield self._insertMockEnv()
        input = Environment2(name="TestEnvironment",description="A test description",status="frozen")
        exp = input
        obs = yield self.environmentSqliteDao.load_environment(id = 1)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_load_all_environments(self):
        yield self._dbpool.runQuery('''
        INSERT into environments VALUES(1,"TestEnvironmentOne","A test description","frozen")''')
        yield self._dbpool.runQuery('''
        INSERT into environments VALUES(2,"TestEnvironmentTwo","Another test description","live")''')
        exp = [Environment2(name="TestEnvironmentOne",description="A test description",status="frozen"),Environment2(name="TestEnvironmentTwo",description="Another test description",status="live")]
        obs = yield self.environmentSqliteDao.load_environments()
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks 
    def _insertMockEnv(self):
       yield self._dbpool.runQuery('''
        INSERT into environments VALUES(1,"TestEnvironment","A test description","frozen")''')