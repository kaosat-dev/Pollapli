from doboz_web.core.persistence.sqlite.sqlite_dao_manager import SqliteDaoManager

class DaoManagerFactory(object):
 
    def create_dao_manager(self,type):
        if type == "sqlite":
            return SqliteDaoManager()
            