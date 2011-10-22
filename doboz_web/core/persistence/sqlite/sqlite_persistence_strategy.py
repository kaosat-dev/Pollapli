from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from doboz_web.core.persistence.persistence_strategy import PersistenceStrategy


class DbStoreFetcher(object):
    pass

#TODO : add some sort of caching method 

class SqlitePersistenceStrategy(PersistenceStrategy):
    def __init__(self):
        self._dbPools = {}
        
        self._dbs = {}
        self._dbs["main"] = "pollapli.db"
        self._mapping = {}
        self._mapping["Update"] = "main"
        self._mapping["Environment"] = "_environment.name"
        self._mapping["Device"] = "_environment.name"
        self._mapping["Task"] = "_environment.name"
        
        self.dispatchCriteria = "_environment.name"
        
    def get_store(self,object,objectType):
        dispatchObjName = self.dispatchCriteria.split(".")[0]
        tmpObj =  object
        while not hasattr(tmpObj,dispatchObjName):
            tmpObj = tmpObj._parent
            
        dispatchObjSub = self.dispatchCriteria.split(".")[1]
        dbName = getattr(getattr(tmpObj,dispatchObjName),dispatchObjSub)
        dbPool = self._dbPools.get(dbName,None)
        if dbPool is None:
            self._dbPools[dbName] = adbapi.ConnectionPool("sqlite3",dbName,check_same_thread=False)
            dbPool = self._dbPools[dbName]
        return dbPool