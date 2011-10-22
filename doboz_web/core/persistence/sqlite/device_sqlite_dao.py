from twisted.internet import reactor, defer
from twisted.python.failure import Failure
from doboz_web.core.persistence.dao_base.device_dao import DeviceDao
from doboz_web.core.logic.components.nodes.node import Device


class DeviceSqliteDao(DeviceDao):
    def __init__(self,dbPool):
        self._dbPool=dbPool
        self._tableCreated = False
    
    @defer.inlineCallbacks
    def _createTable(self):
        if not self._tableCreated:
            try:
                yield self._dbPool.runQuery('''SELECT name FROM devices LIMIT 1''')
            except Exception as inst:
                pass#print("error",inst)
                try:
                    yield self._dbPool.runQuery('''CREATE TABLE devices(
                         id INTEGER PRIMARY KEY,
                         name TEXT,
                         description TEXT,
                         status TEXT NOT NULL DEFAULT "inactive"
                         )''')
                    self._tableCreated = True
                except Exception as inst2:
                    print("error2",inst2)
                
    
    def _execute_txn(self, txn, query,*args,**kwargs):
        txn.execute(query, args)
        result = txn.fetchall()
        return result
    
    @defer.inlineCallbacks
    def load_device(self,id = -1, *args,**kwargs):
        """Retrieve data from device object."""
        yield self._createTable()
        rows = yield self._dbPool.runQuery("SELECT name,description,status FROM devices WHERE id = ?", str(id))
        result=None
        if len(rows)>0:
            name,description,status = rows[0]
            result = Device(name = name,description=description,status=status)
        defer.returnValue(result)
        
    @defer.inlineCallbacks
    def save_device(self, device):
        """Save the device object ."""
        yield self._createTable()
        if hasattr(device,"_id"):
            #print ("updating device with id %s, called %s" %(str(device._id),device.name))
            yield self._dbPool.runQuery('''UPDATE devices SET name = ? ,description = ?, status= ? WHERE id = ? ''', (device.name,device.description,device.status,device._id))
        else:
            def txnExec(txn):
                txn.execute('''INSERT into devices VALUES(null,?,?,?)''', (device.name,device.description,device.status))
                result = txn.fetchall()
                txn.execute("SELECT last_insert_rowid()")
                result = txn.fetchall()
                device._id = result[0][0]
                        
            yield self._dbPool.runInteraction(txnExec)
            defer.returnValue(True)
    
    @defer.inlineCallbacks
    def save_devices(self,lDevices):
        for device in lDevices:
            yield self.save_device(device)
    
    @defer.inlineCallbacks
    def load_devices(self,*args,**kwargs):
        """Save the device object ."""
        yield self._createTable()
        lDevices = []
        result = yield self._dbPool.runQuery("SELECT name,description,status FROM devices ORDER by id")
        for row in result:
            name,description,status = row
            lDevices.append(Device(name = name,description=description,status=status))
        defer.returnValue(lDevices)