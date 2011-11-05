from twisted.internet import reactor, defer,task
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.web import client
from pollapli.core.persistence.dao_base.task_dao import TaskDao

class TaskSqliteDao(TaskDao):
    def __init__(self,dbPool):
        self._dbPool = dbPool
        self._tableCreated = False
                  
    @defer.inlineCallbacks
    def _createTable(self):
        if not self._tableCreated:
            try:
                yield self._dbPool.runQuery('''SELECT name FROM devices LIMIT 1''')
            except Exception as inst:
                pass#print("error",inst)
                try:
                    yield self._dbPool.runQuery('''CREATE TABLE updates(
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
                except Exception as inst2:
                    print("error2",inst2)
    
        
    @defer.inlineCallbacks
    def load_update(self,id = -1, *args,**kwargs):
        yield self._createTable()
        """Retrieve data from update object."""
        rows = yield self._dbPool.runQuery("SELECT type, name, description, version, tags, downloadUrl, enabled FROM updates WHERE id = ?", str(id))
        type, name, description, version, tags, downloadUrl, enabled = rows[0]
        defer.returnValue( Update2(type = type, name = name, description = description,version = version, tags = tags.split(","), downloadUrl = downloadUrl, enabled = enabled))
    
    @defer.inlineCallbacks
    def load_updates(self,*args,**kwargs):
        """Retrieve all update objects."""
        yield self._createTable()
        lUpdates = []
        result = yield self._dbPool.runQuery("SELECT type, name, description, version, tags, downloadUrl, enabled  FROM updates ORDER by id")
        for row in result:
            type, name, description, version, tags, downloadUrl, enabled = row
            lUpdates.append(Update2(type = type, name = name, description = description,version = version, tags = tags.split(","), downloadUrl = downloadUrl, enabled = enabled))
        defer.returnValue(lUpdates)
    
    @defer.inlineCallbacks
    def save_update(self, update):
        yield self._createTable()
        """Save the update object ."""
        if hasattr(update,"_id"):
            #print ("updating update with id %s, called %s" %(str(update._id),update.name))
            yield self._dbPool.runQuery('''UPDATE updates SET type = ?, name = ? ,description = ?, version = ?, tags = ? , downloadUrl = ?, enabled = ? WHERE id = ? ''', \
                                        (update.type,update.name,update.description,update.version,",".join(update.tags),update.downloadUrl,update.enabled,update._id))
        else:
            def txnExec(txn):
                txn.execute('''INSERT into updates VALUES(null,?,?,?,?,?,?,?)''', (update.type,update.name,update.description,\
                                                                                   update.version,",".join(update.tags),update.downloadUrl,update.enabled))
                result = txn.fetchall()
                txn.execute("SELECT last_insert_rowid()")
                result = txn.fetchall()
                update._id = result[0][0]
                        
            yield self._dbPool.runInteraction(txnExec)
            defer.returnValue(True)
            
    @defer.inlineCallbacks
    def save_updates(self, lUpdates):
        yield self._createTable()
        for update in lUpdates:
            yield self.save_update(update)
        
    
   
    