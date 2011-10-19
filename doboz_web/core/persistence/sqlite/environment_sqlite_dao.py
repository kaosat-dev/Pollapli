from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from doboz_web.core.persistence.dao_base.environment_dao import EnvironmentDao
from doboz_web.core.logic.components.environments.environment import Environment2

#TODO: make these more generic (not the interface, the implementation)
class EnvironmentSqliteDao(EnvironmentDao):
    def __init__(self,dbPool):
        self._dbPool=dbPool
        
    @defer.inlineCallbacks 
    def load_environment(self,id=-1,*args,**kwargs):
        """Retrieve data from environment object."""
        result = yield self._dbPool.runQuery("SELECT name,description,status FROM environments WHERE id = ?", str(id))
        name,description,status = result[0]
        defer.returnValue( Environment2(name = name,description=description,status=status))
       
    @defer.inlineCallbacks 
    def load_environments(self,*args,**kwargs):
        """Retrieve multiple environment objects."""
        lEnvironments = []
        result = yield self._dbPool.runQuery("SELECT name,description,status FROM environments ORDER by id")
        for row in result:
            name,description,status = row
            lEnvironments.append(Environment2(name = name,description=description,status=status))
        defer.returnValue(lEnvironments)
            
    @defer.inlineCallbacks 
    def save_environment(self, environment):
        """Save the environment object ."""
        if hasattr(environment,"_id"):
            #print ("updating environment with id %s, called %s" %(str(environment._id),environment.name))
            yield self._dbPool.runQuery('''UPDATE environments SET name = ? ,description = ?, status= ? WHERE id = ? ''', (environment.name,environment.description,environment.status,environment._id))
        else:
            def txnExec(txn):
                txn.execute('''INSERT into environments VALUES(null,?,?,?)''', (environment.name,environment.description,environment.status))
                result = txn.fetchall()
                txn.execute("SELECT last_insert_rowid()")
                result = txn.fetchall()
                environment._id = result[0][0]
                        
            yield self._dbPool.runInteraction(txnExec)
            defer.returnValue(True)
        
        