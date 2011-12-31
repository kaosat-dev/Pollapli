import uuid
from twisted.internet import reactor, defer,task
from twisted.python import log,failure
from pollapli.core.persistence.dao_base.update_dao import UpdateDao
from pollapli.core.logic.components.packages.package import Package
from pollapli.exceptions import PackageNotFound

class UpdateSqliteDao(UpdateDao):
    def __init__(self,db_pool=None, persistenceStrategy =None):
        self._db_pool = db_pool
        self._persistenceStrategy = persistenceStrategy
        self._table_created = False
             
    def _get_last_insertId(self, txn):
        txn.execute("SELECT last_insert_rowid()")
        result = txn.fetchall()
        return result[0][0]
    
    def _execute_txn(self, txn, query, *args,**kwargs):
        if not self._table_created:
            try:
                txn.execute('''SELECT name FROM updates LIMIT 1''')
            except Exception as inst:
                #print("error in load device first step",inst)
                try:
                    txn.execute('''CREATE TABLE updates(
                     id INTEGER PRIMARY KEY,
                     uid INTEGER,
                     type TEXT NOT NULL DEFAULT "update",
                     name TEXT,
                     description TEXT,
                     version TEXT,
                     tags TEXT,
                     downloadUrl TEXT,
                     enabled TEXT NOT NULL DEFAULT "False"
                     )''')
                    self._table_created = True
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
            query = query or '''SELECT uid,type,name,description,version,tags,downloadUrl,enabled FROM updates WHERE uid = ?'''
            args= [id]
        else:
            query = query or '''SELECT uid,type,name,description,version,tags,downloadUrl,enabled FROM updates '''
        if order is not None:
            query = query + " ORDER BY %s" %(str(order))
        args = args
        return self._db_pool.runInteraction(self._select,query,args)
       
    def insert(self,tableName=None, query=None, args=None):  
        query = query or '''INSERT into updates VALUES(null,?,?,?,?,?,?,?,?)''' 
        args = args
        return self._db_pool.runInteraction(self._insert,query,args)
    
    def update(self,tableName=None,query=None,args=None):  
        query = query or '''UPDATE updates SET type = ?, name = ? ,description = ?, version = ?, tags = ? , downloadUrl = ?, enabled = ? WHERE id = ? ''' 
        args = args
        return self._db_pool.runInteraction(self._update,query,args)
    
    @defer.inlineCallbacks
    def load_update(self,id = None, *args,**kwargs):
        """Retrieve data from update object."""
        rows = yield self.select(id = str(id))   
        result=None
        if len(rows)>0:    
            id, type, name, description, version, tags, downloadUrl, enabled = rows[0]
            result =  Update(type = type, name = name, description = description,version = version, tags = tags.split(","), downloadUrl = downloadUrl, enabled = enabled)
            result.cid = uuid.UUID(id)
        else:
            raise UpdateNotFound()
        defer.returnValue(result)
        
    @defer.inlineCallbacks
    def load_updates(self,*args,**kwargs):
        """Retrieve all update objects."""
        lUpdates = []
        rows = yield self.select(order = "id")
        for row in rows:
            id, type, name, description, version, tags, downloadUrl, enabled = row
            update =Update(type = type, name = name, description = description,version = version, tags = tags.split(","), downloadUrl = downloadUrl, enabled = enabled)
            update.cid = uuid.UUID(id)
            lUpdates.append(update)     
        defer.returnValue(lUpdates)
    
    @defer.inlineCallbacks
    def save_update(self, update):
        """Save the update object ."""
           
        if hasattr(update,"_dbId"):
            yield self.update(args = (update.type,update.name,update.description,update.version,",".join(update.tags),update.downloadUrl,update.enabled,update._dbId))
        else:
            update._dbId = yield self.insert(args = (str(update.cid),update.type,update.name,update.description,update.version,",".join(update.tags),update.downloadUrl,update.enabled))              
         
    @defer.inlineCallbacks
    def save_updates(self, lUpdates):
        for update in lUpdates:
            yield self.save_update(update)
        
    
   
    