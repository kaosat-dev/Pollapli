from twisted.internet import reactor, defer
from twisted.python.failure import Failure
from doboz_web.core.persistence.dao_base.device_dao import DeviceDao
from doboz_web.core.logic.components.nodes.node import Device


class DeviceSqliteDao(DeviceDao):
    def __init__(self,dbPool):
        self._dbPool=dbPool
        self._tableCreated = False
                    
    def _get_last_insertId(self, txn):
        txn.execute("SELECT last_insert_rowid()")
        result = txn.fetchall()
        return result[0][0]
    
    def _execute_txn(self, txn, query, *args,**kwargs):
        if not self._tableCreated:
            try:
                txn.execute('''SELECT name FROM devices LIMIT 1''')
            except Exception as inst:
                #print("error in load device first step",inst)
                try:
                    txn.execute('''CREATE TABLE devices (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT "inactive")''')
                    self._tableCreated = True
                except Exception as inst:
                    print("error in load device second step",inst) 
                    
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
            query = query or '''SELECT name,description,status FROM devices WHERE id = ?'''
            args= id
        else:
            query = query or '''SELECT name,description,status FROM devices '''
       
        if order is not None:
            query = query + " ORDER BY %s" %(str(order))
        args = args
        return self._dbPool.runInteraction(self._select,query,args)
       
    def insert(self,tableName=None, query=None, args=None):  
        query = query or '''INSERT into devices VALUES(null,?,?,?)''' 
        args = args
        return self._dbPool.runInteraction(self._insert,query,args)
    
    def update(self,tableName=None,query=None,args=None):  
        query = query or '''UPDATE devices SET name = ? ,description = ?, status= ? WHERE id = ? ''' 
        args = args
        return self._dbPool.runInteraction(self._update,query,args)
    
    @defer.inlineCallbacks
    def load_device(self,id = -1, *args,**kwargs):
        """Retrieve data from device object."""
        rows =  yield self.select(id = str(id))       
        result=None
        if len(rows)>0:
            name,description,status = rows[0]
            result = Device(name = name,description=description,status=status)
        defer.returnValue(result)
        
    @defer.inlineCallbacks
    def save_device(self, device):
        """Save the device object ."""    
        if hasattr(device,"_id"):
            yield self.update(args = (device.name,device.description,device.status,device._id))
        else:
            device._id = yield self.insert(args = (device.name,device.description,device.status))                            
            
    @defer.inlineCallbacks
    def save_devices(self,lDevices):
        for device in lDevices:
            yield self.save_device(device)
    
    @defer.inlineCallbacks
    def load_devices(self,*args,**kwargs):
        """Save the device object ."""
        lDevices = []
        rows = yield self.select(order = "id")
        for row in rows:
            name,description,status = row
            lDevices.append(Device(name = name,description=description,status=status))
        defer.returnValue(lDevices)