import uuid,logging
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.persistence.dao_base.device_dao import DeviceDao
from pollapli.core.logic.components.devices.device import Device
from pollapli.exceptions import DeviceNotFound

class DeviceSqliteDao(DeviceDao):
    def __init__(self,dbPool=None,persistenceStrategy=None):
        self._dbPool=dbPool
        #self._persistenceStrategy = persistenceStrategy
        self._tableCreated = False
                    
    def _get_last_insertId(self, txn):
        txn.execute("SELECT last_insert_rowid()")
        result = txn.fetchall()
        return result[0][0]
    
    def _execute_txn(self, txn, query, *args,**kwargs):
        #if not self._tableCreated:
            try:
                txn.execute('''SELECT name FROM devices ''')
            except Exception as inst:
                log.msg("error in load device first step",inst, logLevel=logging.CRITICAL)
                try:
                    txn.execute('''CREATE TABLE devices (
                    id INTEGER PRIMARY KEY,
                    uid INTEGER ,
                    name TEXT,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT "inactive",
                    environment_uid INTEGER 
                    )''')
                    self._tableCreated = True
                except Exception as inst:
                    log.msg("error in load device second step",inst, logLevel=logging.CRITICAL)
                   
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
    
    def select(self, tableName=None, id=None, environmentId=None, query=None, order=None, *args,**kwargs):  
        if id is not None:
            query = query or '''SELECT uid,name,description,status FROM devices WHERE uid = ?'''
            args= [id]
        elif environmentId is not None:
            query = query or '''SELECT uid,name,description,status FROM devices WHERE environment_uid = ?'''
            args= [environmentId]
        else:
            query = query or '''SELECT uid,name,description,status FROM devices '''
       
        if order is not None:
            query = query + " ORDER BY %s" %(str(order))
        
        return self._dbPool.runInteraction(self._select,query,args)
       
    def insert(self,tableName=None, query=None, args=None):  
        query = query or '''INSERT into devices VALUES(null,?,?,?,?,?)''' 
        args = args
        return self._dbPool.runInteraction(self._insert,query,args)
    
    def update(self,tableName=None,query=None,args=None):  
        query = query or '''UPDATE devices SET name = ? ,description = ?, status = ?, environment_uid = ? WHERE id = ? ''' 
        args = args
        return self._dbPool.runInteraction(self._update,query,args)
    
    def delete(self,id=None,tableName=None,query=None,args=None):  
        args=[id]
        query = query or '''DELETE FROM devices WHERE id = ? '''
        return self._dbPool.runInteraction(self._execute_txn,query,args)
    
    @defer.inlineCallbacks
    def load_device(self,id = None, environmentId = None ,*args,**kwargs):
        """Retrieve data from device object."""
        if id is not None: 
            rows =  yield self.select(id = str(id)) 
        elif environmentId is not None:
            rows =  yield self.select(environmentId = str(environmentId))       
        result=None
        if len(rows)>0:
            id,name,description,status = rows[0]
            result = Device(name = name,description=description,status=status)
            result._id = uuid.UUID(id)
        else:
            raise DeviceNotFound()
        defer.returnValue(result)
    
    @defer.inlineCallbacks
    def load_devices(self, environmentId = None ,*args,**kwargs):
        """Save the device object ."""
        lDevices = []
        if environmentId is not None:
            rows = yield self.select(environmentId = str(environmentId), order = "id")
        else:
            rows = yield self.select(order = "id")
        for row in rows:
            id,name,description,status = row
            device = Device(name = name,description=description,status=status)
            device._id = uuid.UUID(id)
            lDevices.append(device)
        defer.returnValue(lDevices)
        
    @defer.inlineCallbacks
    def save_device(self, device):
        """Save the device object ."""  
        parentEnvironment = device._parent 
        parentUId = None
        if parentEnvironment is not None:
            parentUId = parentEnvironment._id
            
        if hasattr(device,"_dbId"):
            yield self.update(args = (device.name,device.description,device._status,str(parentUId),device._dbId))
        else:
            device._dbId = yield self.insert(args = (str(device._id),device.name,device.description,device._status,str(parentUId)))                            
            
    @defer.inlineCallbacks
    def save_devices(self,lDevices):
        for device in lDevices:
            yield self.save_device(device)
            
    @defer.inlineCallbacks 
    def delete_device(self, device):
        """Delete a device object ."""
        if hasattr(device,"_dbId"):
            yield self.delete(device._dbId)
            delattr(device,"_dbId")
        else:
            raise DeviceNotFound()