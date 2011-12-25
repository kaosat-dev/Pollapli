from twisted.internet import reactor, defer
from twisted.python.failure import Failure
from pollapli.core.persistence.dao_base.driver_dao import DriverDao
from pollapli.core.logic.components.nodes.node import Device


class DriverSqliteDao(DriverDao):
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
                txn.execute('''SELECT name FROM drivers LIMIT 1''')
            except Exception as inst:
                #print("error in load driver first step",inst)
                try:
                    txn.execute('''CREATE TABLE drivers (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT "inactive")''')
                    self._tableCreated = True
                except Exception as inst:
                    print("error in load driver second step",inst) 
                    
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
            query = query or '''SELECT name,description,status FROM drivers WHERE id = ?'''
            args= id
        else:
            query = query or '''SELECT name,description,status FROM drivers '''
       
        if order is not None:
            query = query + " ORDER BY %s" %(str(order))
        args = args
        return self._dbPool.runInteraction(self._select,query,args)
       
    def insert(self,tableName=None, query=None, args=None):  
        query = query or '''INSERT into drivers VALUES(null,?,?,?)''' 
        args = args
        return self._dbPool.runInteraction(self._insert,query,args)
    
    def update(self,tableName=None,query=None,args=None):  
        query = query or '''UPDATE drivers SET name = ? ,description = ?, status= ? WHERE id = ? ''' 
        args = args
        return self._dbPool.runInteraction(self._update,query,args)
    
    @defer.inlineCallbacks
    def load_driver(self,id = None, *args,**kwargs):
        """Retrieve data from driver object."""
        rows =  yield self.select(id = str(id))       
        result=None
        if len(rows)>0:
            name,description,status = rows[0]
            result = Device(name = name,description=description,status=status)
        defer.returnValue(result)
        
    @defer.inlineCallbacks
    def save_driver(self, driver):
        """Save the driver object ."""    
        if hasattr(driver,"cid"):
            yield self.update(args = (driver.name,driver.description,driver.status,driver.cid))
        else:
            driver.cid = yield self.insert(args = (driver.name,driver.description,driver.status))                            
            
    @defer.inlineCallbacks
    def save_drivers(self,lDevices):
        for driver in lDevices:
            yield self.save_driver(driver)
    
    @defer.inlineCallbacks
    def load_drivers(self,*args,**kwargs):
        """Save the driver object ."""
        lDevices = []
        rows = yield self.select(order = "id")
        for row in rows:
            name,description,status = row
            lDevices.append(Device(name = name,description=description,status=status))
        defer.returnValue(lDevices)