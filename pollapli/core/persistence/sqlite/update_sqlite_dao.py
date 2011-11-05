from twisted.internet import reactor, defer,task
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.web import client
from pollapli.core.persistence.dao_base.update_dao import UpdateDao
from pollapli.core.logic.components.updates.update import Update

class UpdateSqliteDao(UpdateDao):
    def __init__(self,dbPool=None, persistenceStrategy =None):
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
                txn.execute('''SELECT name FROM updates LIMIT 1''')
            except Exception as inst:
                #print("error in load device first step",inst)
                try:
                    txn.execute('''CREATE TABLE updates(
                     id INTEGER PRIMARY KEY,
                     type TEXT NOT NULL DEFAULT "update",
                     name TEXT,
                     description TEXT,
                     version TEXT,
                     tags TEXT,
                     downloadUrl TEXT,
                     enabled TEXT NOT NULL DEFAULT "False"
                     )''')
                    self._tableCreated = True
                except Exception as inst:
                    print("error in load update second step",inst) 
                    
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
            query = query or '''SELECT type, name, description, version, tags, downloadUrl, enabled FROM updates WHERE id = ?'''
            args= id
        else:
            query = query or '''SELECT type, name, description, version, tags, downloadUrl, enabled FROM updates '''
       
        if order is not None:
            query = query + " ORDER BY %s" %(str(order))
        args = args
        return self._dbPool.runInteraction(self._select,query,args)
       
    def insert(self,tableName=None, query=None, args=None):  
        query = query or '''INSERT into updates VALUES(null,?,?,?,?,?,?,?)''' 
        args = args
        return self._dbPool.runInteraction(self._insert,query,args)
    
    def update(self,tableName=None,query=None,args=None):  
        query = query or '''UPDATE updates SET type = ?, name = ? ,description = ?, version = ?, tags = ? , downloadUrl = ?, enabled = ? WHERE id = ? ''' 
        args = args
        return self._dbPool.runInteraction(self._update,query,args)
    
    @defer.inlineCallbacks
    def load_update(self,id = -1, *args,**kwargs):
        """Retrieve data from update object."""
        rows = yield self.select(id = str(id))   
        result=None
        if len(rows)>0:    
            type, name, description, version, tags, downloadUrl, enabled = rows[0]
            result =  Update(type = type, name = name, description = description,version = version, tags = tags.split(","), downloadUrl = downloadUrl, enabled = enabled)
        defer.returnValue(result)
        
    @defer.inlineCallbacks
    def load_updates(self,*args,**kwargs):
        """Retrieve all update objects."""
        lUpdates = []
        rows = yield self.select(order = "id")
        for row in rows:
            type, name, description, version, tags, downloadUrl, enabled = row
            lUpdates.append(Update(type = type, name = name, description = description,version = version, tags = tags.split(","), downloadUrl = downloadUrl, enabled = enabled))
        defer.returnValue(lUpdates)
    
    @defer.inlineCallbacks
    def save_update(self, update):
        """Save the update object ."""
        if hasattr(update,"_id"):
            yield self.update(args = (update.type,update.name,update.description,update.version,",".join(update.tags),update.downloadUrl,update.enabled,update._id))
        else:
            update._id = yield self.insert(args = (update.type,update.name,update.description,update.version,",".join(update.tags),update.downloadUrl,update.enabled))              
         
    @defer.inlineCallbacks
    def save_updates(self, lUpdates):
        for update in lUpdates:
            yield self.save_update(update)
        
    
   
    