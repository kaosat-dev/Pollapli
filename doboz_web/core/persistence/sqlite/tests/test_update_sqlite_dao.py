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
        
        result = yield self._dbpool.runQuery('''SELECT type, name,description,version,tags,downloadUrl,enabled FROM updates WHERE id =  1''')
        type, name, description, version, tags, downloadUrl, enabled = result[0]
        
        exp = input
        obs = Update2(type=type,name=name,description=description,version=version, tags = tags, downloadUrl = downloadUrl, enabled = enabled)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_save_update_existing(self):
        input = Update2(type="update",name="TestUpdate ",description="test description",version="0.0.1",downloadUrl="http://test.com/"\
                   ,tags=["test","alsotest"],enabled=False)
        yield self._updateSqliteDao.save_update(input)
        input.name="TestEnvironmentChanged"
        yield self._updateSqliteDao.save_update(input)
        
        result = yield self._dbpool.runQuery('''SELECT type, name,description,version,tags,downloadUrl,enabled FROM updates WHERE id =  1''')
        type, name, description, version, tags, downloadUrl, enabled = result[0]
        exp=input
        obs = Update2(type=type,name=name,description=description,version=version, tags = tags, downloadUrl = downloadUrl, enabled = enabled)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_save_updates(self):
        input = [
        Update2(type = "update", name="TestUpdate",description="A test description", version="0.0.2",tags=["a tag", "anothertag"],downloadUrl="http://test.test/addon",enabled = True)
        ,Update2(type = "addon", name="TestUpdate2",description="A test description too", version="0.1.2",tags=["anothertag"],downloadUrl="http://test.test/addon",enabled = False)
        ]
        
        yield self._updateSqliteDao.save_updates(input)
        
        expLUpdates=input
        obsLUpdates=[]
        rows = yield self._dbpool.runQuery('''SELECT type, name,description,version,tags,downloadUrl,enabled FROM updates''')
        for row in rows:
            type, name, description, version, tags, downloadUrl, enabled = row
            obsLUpdates.append(Update2(type=type,name=name,description=description,version=version, tags = tags, downloadUrl = downloadUrl, enabled = enabled))
        
        self.assertEquals(obsLUpdates,expLUpdates)
        
    @defer.inlineCallbacks
    def test_load_updatebyid(self):    
        yield self._insert_mockupdate()
        obs = yield self._updateSqliteDao.load_update(id = 1)
        exp = Update2(type = "addon", name="TestUpdate",description="A test description", version="0.0.2",tags=["a tag", "anothertag"],downloadUrl="http://test.test/addon",enabled = True)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_load_updates(self):
        yield self._insert_multiple_mockupdates()
        input = [
        Update2(type = "update", name="TestUpdate",description="A test description", version="0.0.2",tags=["a tag", "anothertag"],downloadUrl="http://test.test/addon",enabled = True)
        ,Update2(type = "addon", name="TestUpdate2",description="A test description too", version="0.1.2",tags=["anothertag"],downloadUrl="http://test.test/addon",enabled = False)
        ]
        exp = input
        obs = yield self._updateSqliteDao.load_updates()
        self.assertEquals(obs,exp)
            
    @defer.inlineCallbacks 
    def _insert_mockupdate(self):
        yield self._updateSqliteDao._createTable()
        yield self._dbpool.runQuery('''
        INSERT into updates VALUES(null,"addon","TestUpdate","A test description","0.0.2","a tag, anothertag","http://test.test/addon","True")''')
    
    @defer.inlineCallbacks 
    def _insert_multiple_mockupdates(self):
        yield self._updateSqliteDao._createTable()
        yield self._dbpool.runQuery('''
        INSERT into updates VALUES(null,"update","TestUpdate","A test description","0.0.2","a tag, anothertag","http://test.test/update","True")''')
        yield self._dbpool.runQuery('''
        INSERT into updates VALUES(null,"addon","TestUpdate2","A test description too","0.1.2","anothertag","http://test.test/addon","False")''')
        


  
    