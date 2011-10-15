from doboz_web.core.persistance.sqlite.update_sqlite_dao import UpdateSqliteDao
from doboz_web.core.persistance.sqlite.environment_sqlite_dao import EnvironmentSqliteDao
from doboz_web.core.persistance.sqlite.node_sqlite_dao import NodeSqliteDao

class PersistanceLayer(object):
    def __init__(self):
        self._updateDao=UpdateSqliteDao()
        self._environmentDao=EnvironmentSqliteDao()
        self._nodeDao=NodeSqliteDao()
        
    def __getattr__(self, attr_name):
        if hasattr(self._updateDao, attr_name):
            return getattr(self._updateDao, attr_name)
        elif hasattr(self._environmentDao, attr_name):
            return getattr(self._environmentDao, attr_name)
        elif hasattr(self._nodeDao, attr_name):
            return getattr(self._nodeDao, attr_name)
        else:
            raise AttributeError(attr_name)