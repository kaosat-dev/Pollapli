import os
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.trial import unittest
from doboz_web.core.persistence.sqlite.update_sqlite_dao import UpdateSqliteDao
from doboz_web.core.logic.components.updates.update_manager import Update2

class UpdateSqliteDaoTests(unittest.TestCase):
    
    def setUp(self):
        self._dbpool = adbapi.ConnectionPool("sqlite3",'pollapli.db',check_same_thread=False)
        self._updateSqliteDao = UpdateSqliteDao(self._dbpool)
        
    @defer.inlineCallbacks
    def tearDown(self):
        yield self._dbpool.close()
        os.remove('pollapli.db')
    
    @defer.inlineCallbacks
    def test_save_update_new(self):
        input = Update2(type="update",name="TestUpdate ",description="test description",version="0.0.1",downloadUrl="http://test.com/"\
                   ,tags=["test","alsotest"],enabled=False)
        yield self._updateSqliteDao.save_update(input)
                
        exp = input
        obs = yield self._updateSqliteDao.load_update(id = 1)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_save_update_existing(self):
        input = Update2(type="update",name="TestUpdate ",description="test description",version="0.0.1",downloadUrl="http://test.com/"\
                   ,tags=["test","alsotest"],enabled=False)
        yield self._updateSqliteDao.save_update(input)
        input.name="TestEnvironmentChanged"
        yield self._updateSqliteDao.save_update(input)
        
        exp=input
        obs = yield self._updateSqliteDao.load_update(id = 1)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_save_updates(self):
        input = [
        Update2(type = "update", name="TestUpdate",description="A test description", version="0.0.2",tags=["a tag", "anothertag"],downloadUrl="http://test.test/addon",enabled = True)
        ,Update2(type = "addon", name="TestUpdate2",description="A test description too", version="0.1.2",tags=["anothertag"],downloadUrl="http://test.test/addon",enabled = False)
        ]
        yield self._updateSqliteDao.save_updates(input)
        
        expLUpdates = input
        obsLUpdates = yield self._updateSqliteDao.load_updates()
        self.assertEquals(obsLUpdates,expLUpdates)
        
    @defer.inlineCallbacks
    def test_load_updatebyid(self):    
        input = Update2(type = "update", name="TestUpdate",description="A test description", version="0.0.2",tags=["a tag", "anothertag"],downloadUrl="http://test.test/addon",enabled = True)
        yield self._updateSqliteDao.save_update(input)
        
        exp = input
        obs = yield self._updateSqliteDao.load_update(id = 1)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_load_updates(self):
        input = [
        Update2(type = "update", name="TestUpdate",description="A test description", version="0.0.2",tags=["a tag", "anothertag"],downloadUrl="http://test.test/addon",enabled = True)
        ,Update2(type = "addon", name="TestUpdate2",description="A test description too", version="0.1.2",tags=["anothertag"],downloadUrl="http://test.test/addon",enabled = False)
        ]
        yield self._updateSqliteDao.save_updates(input)
        exp = input
        obs = yield self._updateSqliteDao.load_updates()
        self.assertEquals(obs,exp)
            
    