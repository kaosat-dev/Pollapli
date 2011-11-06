import uuid,logging
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.persistence.dao_base.task_dao import TaskDao
from pollapli.core.logic.components.tasks.task import Task
from pollapli.exceptions import TaskNotFound


class TaskSqliteDao(TaskDao):
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
                txn.execute('''SELECT name FROM tasks ''')
            except Exception as inst:
                log.msg("error in load task first step",inst, logLevel=logging.CRITICAL)
                try:
                    txn.execute('''CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY,
                    uid INTEGER ,
                    name TEXT,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT "inactive",
                    environment_uid INTEGER 
                    )''')
                    self._tableCreated = True
                except Exception as inst:
                    log.msg("error in load task second step",inst, logLevel=logging.CRITICAL)
                   
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
            query = query or '''SELECT uid,name,description,status FROM tasks WHERE uid = ?'''
            args= [id]
        elif environmentId is not None:
            query = query or '''SELECT uid,name,description,status FROM tasks WHERE environment_uid = ?'''
            args= [environmentId]
        else:
            query = query or '''SELECT uid,name,description,status FROM tasks '''
       
        if order is not None:
            query = query + " ORDER BY %s" %(str(order))
        
        return self._dbPool.runInteraction(self._select,query,args)
       
    def insert(self,tableName=None, query=None, args=None):  
        query = query or '''INSERT into tasks VALUES(null,?,?,?,?,?)''' 
        args = args
        return self._dbPool.runInteraction(self._insert,query,args)
    
    def update(self,tableName=None,query=None,args=None):  
        query = query or '''UPDATE tasks SET name = ? ,description = ?, status = ?, environment_uid = ? WHERE id = ? ''' 
        args = args
        return self._dbPool.runInteraction(self._update,query,args)
    
    def delete(self,id=None,tableName=None,query=None,args=None):  
        args=[id]
        query = query or '''DELETE FROM tasks WHERE id = ? '''
        return self._dbPool.runInteraction(self._execute_txn,query,args)
    
    @defer.inlineCallbacks
    def load_task(self,id = None, environmentId = None ,*args,**kwargs):
        """Retrieve data from task object."""
        if id is not None: 
            rows =  yield self.select(id = str(id)) 
        elif environmentId is not None:
            rows =  yield self.select(environmentId = str(environmentId))       
        result=None
        if len(rows)>0:
            id,name,description,status = rows[0]
            result = Task(name = name,description=description,status=status)
            result._id = uuid.UUID(id)
        else:
            raise TaskNotFound()
        defer.returnValue(result)
    
    @defer.inlineCallbacks
    def load_tasks(self, environmentId = None ,*args,**kwargs):
        """Save the task object ."""
        lTasks = []
        if environmentId is not None:
            rows = yield self.select(environmentId = str(environmentId), order = "id")
        else:
            rows = yield self.select(order = "id")
        for row in rows:
            id,name,description,status = row
            task = Task(name = name,description=description,status=status)
            task._id = uuid.UUID(id)
            lTasks.append(task)
        defer.returnValue(lTasks)
        
    @defer.inlineCallbacks
    def save_task(self, task):
        """Save the task object ."""  
        parentEnvironment = task._parent 
        parentUId = None
        if parentEnvironment is not None:
            parentUId = parentEnvironment._id
            
        if hasattr(task,"_dbId"):
            yield self.update(args = (task._name,task._description,task._status,str(parentUId),task._dbId))
        else:
            task._dbId = yield self.insert(args = (str(task._id),task._name,task._description,task._status,str(parentUId)))                            
            
    @defer.inlineCallbacks
    def save_tasks(self,lTasks):
        for task in lTasks:
            yield self.save_task(task)
            
    @defer.inlineCallbacks 
    def delete_task(self, task):
        """Delete a task object ."""
        if hasattr(task,"_dbId"):
            yield self.delete(task._dbId)
            delattr(task,"_dbId")
        else:
            raise TaskNotFound()