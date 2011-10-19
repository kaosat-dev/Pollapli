from twisted.internet import reactor, defer,task
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from twisted.web import client
from doboz_web.core.persistence.dao_base.update_dao import UpdateDao
from doboz_web.core.logic.components.updates.update_manager import Update2

class UpdateSqliteDao(UpdateDao):
    def __init__(self,dbPool):
        self._dbPool=dbPool
         
    @defer.inlineCallbacks
    def load_update(self,id = -1, *args,**kwargs):
        """Retrieve data from update object."""
        rows = yield self._dbPool.runQuery("SELECT type, name, description, version, tags, downloadUrl, enabled FROM updates WHERE id = ?", str(id))
        type, name, description, version, tags, downloadUrl, enabled = rows[0]
        defer.returnValue( Update2(type = type, name = name, description = description,version = version, tags = tags.split(","), downloadUrl = downloadUrl, enabled = enabled))
    
    @defer.inlineCallbacks
    def load_updates(self,*args,**kwargs):
        """Retrieve all update objects."""
        lUpdates = []
        result = yield self._dbPool.runQuery("SELECT type, name, description, version, tags, downloadUrl, enabled  FROM updates ORDER by id")
        for row in result:
            type, name, description, version, tags, downloadUrl, enabled = row
            lUpdates.append(Update2(type = type, name = name, description = description,version = version, tags = tags.split(","), downloadUrl = downloadUrl, enabled = enabled))
        defer.returnValue(lUpdates)
    
    @defer.inlineCallbacks
    def save_update(self, update):
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
        for update in lUpdates:
            yield self.save_update(update)
        
    
   
    