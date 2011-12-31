import os
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from pollapli.core.persistence.sqlite.update_sqlite_dao import UpdateSqliteDao
from pollapli.core.persistence.sqlite.environment_sqlite_dao import EnvironmentSqliteDao
from pollapli.core.persistence.sqlite.device_sqlite_dao import DeviceSqliteDao
from pollapli.core.persistence.sqlite.task_sqlite_dao import TaskSqliteDao
from pollapli.core.persistence.sqlite.sqlite_persistence_strategy import SqlitePersistenceStrategy

class SqliteDaoManager(object):
    """Main manager for sqlite daos"""
    def __init__(self, pathManager = None):
        self._path_manager = pathManager
        self._persistenceStrategy = SqlitePersistenceStrategy()
        self._db_pool = adbapi.ConnectionPool("sqlite3","pollapli.db",check_same_thread=False)
        self._updateDao = UpdateSqliteDao(db_pool = self._db_pool,persistenceStrategy = self._persistenceStrategy)
        self._environmentDao = EnvironmentSqliteDao(db_pool = self._db_pool, persistenceStrategy = self._persistenceStrategy)
        self._deviceDao = DeviceSqliteDao(db_pool = self._db_pool, persistenceStrategy = self._persistenceStrategy)
        self._taskDao = TaskSqliteDao(db_pool = self._db_pool)
        
    def __getattr__(self, attr_name):
        if hasattr(self._updateDao, attr_name):
            return getattr(self._updateDao, attr_name)
        elif hasattr(self._environmentDao, attr_name):
            return getattr(self._environmentDao, attr_name)
        elif hasattr(self._deviceDao, attr_name):
            return getattr(self._deviceDao, attr_name)
        elif hasattr(self._taskDao, attr_name):
            return getattr(self._taskDao, attr_name)
        else:
            raise AttributeError(attr_name)
    
    @defer.inlineCallbacks
    def tearDown(self):
        yield self._db_pool.close()