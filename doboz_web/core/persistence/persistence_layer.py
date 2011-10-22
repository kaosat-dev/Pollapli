from doboz_web.core.persistence.dao_base.dao_manager_factory import DaoManagerFactory


class PersistenceLayer(object):
    def __init__(self):
       self._daoManager = DaoManagerFactory().create_dao_manager("sqlite")
       
    def __getattr__(self, attr_name):
        if hasattr(self._daoManager, attr_name):
            return getattr(self._daoManager, attr_name)  
        else:
            raise AttributeError(attr_name)
        
        
