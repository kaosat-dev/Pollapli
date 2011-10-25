from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from doboz_web.core.persistence.persistence_strategy import PersistenceStrategy


class DbStoreNameFetcher(object):
    """Helper class that gets the name of the dbpool to use"""
    def fetch(self):
        pass

class SimpleFetcher(DbStoreNameFetcher):
    def __init__(self,dbName):
        self._dbName = dbName
        
    def fetch(self,*args,**kwargs):
        return self._dbName

class ClassAndFieldFetcher(DbStoreNameFetcher):
    def __init__(self,className, fieldName):
        self._className = className
        self._fieldName = fieldName
        
    #TODO: add error handling
    def fetch(self, object):
        currentObj = object
        try:
            while not currentObj.__class__.__name__ == self._className: 
                currentObj = currentObj._parent
        except Exception : pass
            
        dbName = getattr(currentObj,self._fieldName,None)
        print("dbName",dbName)
        return dbName
        
#        dispatchObjName = self.dispatchCriteria.split(".")[0]
#        tmpObj =  object
#        while not hasattr(tmpObj,dispatchObjName):
#            tmpObj = tmpObj._parent
#            
#        dispatchObjSub = self.dispatchCriteria.split(".")[1]
#        dbName = getattr(getattr(tmpObj,dispatchObjName),dispatchObjSub)
#        dbPool = self._dbPools.get(dbName,None)

#TODO: add some sort of caching method 
class SqlitePersistenceStrategy(PersistenceStrategy):
    def __init__(self,defaultBaseName = "pollapli"):
        self._dbPools = {}
        
        self._mapping = {}
        self._mapping["default"] = SimpleFetcher("pollapli")
        self._mapping["Update"] = SimpleFetcher("pollapli")
        self._mapping["Environment2"] = ClassAndFieldFetcher("Environment2","name")
        self._mapping["Device"] = ClassAndFieldFetcher("Environment2","name")
        self._mapping["Task"] = ClassAndFieldFetcher("Environment2","name")
        
    def get_store(self,object,objectType):
        dbName = self._mapping[objectType].fetch(object)
        dbName = "%s.db" %(dbName)
        dbPool = self._dbPools.get(dbName,None)
        if dbPool is None:
            self._dbPools[dbName] =  adbapi.ConnectionPool("sqlite3",dbName,check_same_thread=False)
            dbPool = self._dbPools[dbName]
            
        return dbPool
    
    @defer.inlineCallbacks
    def tear_down(self):
        for dbPool in self._dbPools.values():
            yield dbPool.close()