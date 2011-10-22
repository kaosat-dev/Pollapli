import os
from twisted.enterprise import adbapi 
from doboz_web.core.persistence.sqlite.update_sqlite_dao import UpdateSqliteDao
from doboz_web.core.persistence.sqlite.environment_sqlite_dao import EnvironmentSqliteDao
from doboz_web.core.persistence.sqlite.device_sqlite_dao import DeviceSqliteDao
from doboz_web.core.logic.tools.file_manager import FileManager

#TODO add "persistance hierarchy" class (what goes where)
class SqliteDaoManager(object):
    def __init__(self):
        self._dbpool = adbapi.ConnectionPool("sqlite3", os.path.join(FileManager.rootPath,'pollapli.db'))
        self._updateDao=UpdateSqliteDao(dbPool = self._dbpool)
        self._environmentDao=EnvironmentSqliteDao(dbPool = self._dbpool)
        self._nodeDao=DeviceSqliteDao(dbPool = self._dbpool)
        
    def __getattr__(self, attr_name):
        if hasattr(self._updateDao, attr_name):
            return getattr(self._updateDao, attr_name)
        elif hasattr(self._environmentDao, attr_name):
            return getattr(self._environmentDao, attr_name)
        elif hasattr(self._nodeDao, attr_name):
            return getattr(self._nodeDao, attr_name)
        else:
            raise AttributeError(attr_name)
    