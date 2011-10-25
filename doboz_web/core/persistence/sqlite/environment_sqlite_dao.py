from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from doboz_web.core.persistence.dao_base.environment_dao import EnvironmentDao
from doboz_web.core.logic.components.environments.environment import Environment2

#TODO: make these more generic (not the interface, the implementation)
class EnvironmentSqliteDao(EnvironmentDao):
    def __init__(self,dbPool, persistenceStrategy =None):
        self._dbPool = dbPool
        self._persistenceStrategy = persistenceStrategy
        self._tableCreated = False
        
    def _get_last_insertId(self, txn):
        txn.execute("SELECT last_insert_rowid()")
        result = txn.fetchall()
        return result[0][0]
    
    def _execute_txn(self, txn, query, *args,**kwargs):
        if not self._tableCreated:
            try:
                txn.execute('''SELECT name FROM environments LIMIT 1''')
            except Exception as inst:
                #print("error in load device first step",inst)
                try:
                    txn.execute('''CREATE TABLE environments (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT "frozen")''')
                    self._tableCreated = True
                except Exception as inst:
                    print("error in load environment second step",inst) 
                    
        return txn.execute(query, *args,**kwargs)
    
    def _select(self,txn,query=None,*args):
        self._execute_txn(txn, query,*args)
        return txn.fetchall()
    
    def _insert(self,txn,query=None,*args):
        self._execute_txn(txn,query,*args)
        return self._get_last_insertId(txn)
    
    def _update(self,txn,query=None,*args):
        self._execute_txn(txn, query,*args)
        return None
    
    def select(self,tableName=None, id=None,query=None,order=None,*args):  
        if id is not None:
            query = query or '''SELECT name,description,status FROM environments WHERE id = ?'''
            args= id
        else:
            query = query or '''SELECT name,description,status FROM environments '''
       
        if order is not None:
            query = query + " ORDER BY %s" %(str(order))
        args = args
        
        return self._dbPool.runInteraction(self._select,query,args)
    
    def _select2(self,txn, id = None, order = None):
        if id is not None:
            query = '''SELECT name,description,status FROM environments WHERE id = ?'''
            args= id
        else:
            query = '''SELECT name,description,status FROM environments '''
       
        if order is not None:
            query = query + " ORDER BY %s" %(str(order))
        self._execute_txn(txn, query,*args)
        return txn.fetchall()
            
    def _do_query(self,object,objectType,queryFunct,tableName,id,args):
        """generic query wrapper"""
        return self._persistenceStrategy.get_store(object,objectType).runInteraction(self._select2,args)
        
    def insert(self,tableName=None, query=None, args=None):  
        query = query or '''INSERT into environments VALUES(null,?,?,?)''' 
        args = args
        return self._dbPool.runInteraction(self._insert,query,args)
    
    def update(self,tableName=None,query=None,args=None):  
        query = query or '''UPDATE environments SET name = ? ,description = ?, status= ? WHERE id = ? ''' 
        args = args
        return self._dbPool.runInteraction(self._update,query,args)
        
    @defer.inlineCallbacks 
    def load_environment(self,id = None,*args,**kwargs):
        """Retrieve data from environment object."""
        rows =  yield self.select(id = str(id))   
        result = None
        if len(rows)>0:
            name,description,status = rows[0]
            result = Environment2(name = name,description=description,status=status)
        defer.returnValue( result)
       
    @defer.inlineCallbacks 
    def load_environments(self,*args,**kwargs):
        """Retrieve multiple environment objects."""
        lEnvironments = []
        rows = yield self.select(order = "id")
        for row in rows:
            name,description,status = row
            lEnvironments.append(Environment2(name = name,description=description,status=status))
        defer.returnValue(lEnvironments)
            
    @defer.inlineCallbacks 
    def save_environment(self, environment):
        """Save the environment object ."""
        if hasattr(environment,"_id"):
            yield self.update(args = (environment.name,environment.description,environment.status,environment._id))
        else:
            environment._id = yield self.insert(args = (environment.name,environment.description,environment.status))   
    
    @defer.inlineCallbacks 
    def save_environments(self, lEnvironment):
        for environment in lEnvironment:
            yield self.save_environment(environment)