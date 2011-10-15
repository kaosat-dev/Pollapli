from twisted.trial import unittest
from doboz_web.run import *
from doboz_web.core.persistance.sqlite.update_sqlite_dao import UpdateSqliteDao
from doboz_web.core.logic.components.updates.update_manager import Update

#TODO : replace mutual dependency of tests with manual sqlite inserts/selects


class UpdateSqliteDaoTests(unittest.TestCase):
    def setUp(self):
        configure_all() 
        self.updateSqliteDao=UpdateSqliteDao()
        
    def tearDown(self):
        pass
    
    def test_save_update(self):
        exp = Update(type="test",name="test",description="test",version="0.0.1",downloadUrl="http://test.com/"\
                   ,img="img",tags=["test","alsotest"])
        self.updateSqliteDao.save_update(input)
        obs = self.updateSqliteDao.load_update()
        self.assertEquals(obs,exp)
        
    def test_load_updatebyid(self):    
        input = Update(name="update1")
        self.updateSqliteDao.save_update(input)
        exp = input
        obs = self.updateSqliteDao.load_update(id == 1)
        self.assertEquals(obs,exp)

    def test_load_updates(self):
        input = [Update(name="update1"),Update(name="update2")]
        exp = input
        obs = self.updateSqliteDao.load_all_updates()
        self.assertEquals(obs,exp)
    
  
    