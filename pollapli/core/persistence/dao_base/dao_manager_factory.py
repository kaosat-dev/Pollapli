from pollapli.core.persistence.sqlite.sqlite_dao_manager import SqliteDaoManager

class DaoManagerFactory(object):
    def __init__(self, pathManager = None):
        self._pathManager = pathManager
        
    def create_dao_manager(self, type):
        if type == "sqlite":
            return SqliteDaoManager(pathManager = self._pathManager)
            