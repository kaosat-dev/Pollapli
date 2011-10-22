import os
from twisted.enterprise import adbapi 
from doboz_web.core.persistence.sqlite.update_sqlite_dao import UpdateSqliteDao
from doboz_web.core.persistence.sqlite.environment_sqlite_dao import EnvironmentSqliteDao
from doboz_web.core.persistence.sqlite.device_sqlite_dao import DeviceSqliteDao
from doboz_web.core.persistence.sqlite.task_sqlite_dao import TaskSqliteDao

from doboz_web.core.persistence.sqlite.sqlite_persistence_strategy import SqlitePersistenceStrategy
from doboz_web.core.logic.tools.file_manager import FileManager



class SqliteDaoManager(object):
    """Main manager for sqlite daos"""
    def __init__(self):
        self._persistenceStrategy = SqlitePersistenceStrategy()
        self._dbpool = adbapi.ConnectionPool("sqlite3", os.path.join(FileManager.rootPath,'pollapli.db'))
        
        self._updateDao = UpdateSqliteDao(dbPool = self._persistenceStrategy.get_store("Update"))
        
        
        self._environmentDao = EnvironmentSqliteDao(dbPool = self._persistenceStrategy.get_store("Environment"))
        self._deviceDao = DeviceSqliteDao(dbPool = self._persistenceStrategy.get_store("Device"))
        self._taskDao = TaskSqliteDao(dbPool = self._persistenceStrategy.get_store("Task"))
        
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
    