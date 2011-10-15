from twisted.trial import unittest
from doboz_web.run import *
from doboz_web.core.persistance.sqlite.update_sqlite_dao import environmentSqliteDao
from doboz_web.core.logic.components.environments.environment import Environment

#TODO : replace mutual dependency of tests with manual sqlite inserts/selects

class EnvironmentSqliteDaoTests(unittest.TestCase):
    def setUp(self):
        configure_all() 
        self.environmentSqliteDao=environmentSqliteDao()
        
    def tearDown(self):
        pass
    
    def test_save_environment(self):
        exp = Environment(name="test",description="test")
        self.environmentSqliteDao.save_environment(input)
        obs = self.environmentSqliteDao.load_environment()
        self.assertEquals(obs,exp)
        
    def test_load_environmentbyid(self):    
        input = Environment(name="test",description="test")
        self.environmentSqliteDao.save_environment(input)
        exp = input
        obs = self.environmentSqliteDao.load_environment(id == 1)
        self.assertEquals(obs,exp)

    def test_load_environments(self):
        input = [Environment(name="environment1"),Environment(name="environment2")]
        exp = input
        obs = self.environmentSqliteDao.load_all_environments()
        self.assertEquals(obs,exp)