import logging
from twisted.internet import reactor, defer
from twisted.python import log,failure
from pollapli.core.logic.components.tasks.task import Task
from pollapli.exceptions import TaskNotFound
from pollapli.core.logic.tools.signal_system import SignalDispatcher

class TaskManager(object):    
    def __init__(self, parentEnvironment):
        self._parentEnvironment = parentEnvironment
        self._persistenceLayer = parentEnvironment._persistenceLayer
        self._tasks = {}
        self._signal_channel = "task_manager"
        self._signal_dispatcher = SignalDispatcher(self._signal_channel)
        self.signal_channel_prefix = "environment_"+str(self._parentEnvironment.cid)
    
    @defer.inlineCallbacks
    def setup(self):            
        if self._persistenceLayer is None:
            self._persistenceLayer = self._parentEnvironment._persistenceLayer        
        tasks = yield self._persistenceLayer.load_tasks(environmentId = self._parentEnvironment.cid)
        for task in tasks:
            task._parent = self._parentEnvironment
            task._persistenceLayer = self._persistenceLayer
            self._tasks[task.cid] = task
            #yield task.setup()   
        
    def _send_signal(self,signal="",data=None):
        prefix=self.signal_channel_prefix+"."
        self._signal_dispatcher.send_message(prefix+signal,self,data)
    
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of tasks
    """
 
    @defer.inlineCallbacks
    def add_task(self,name="Default Task",description="Default task description",status = "inactive",params={},*args,**kwargs):
        """
        Add a new task to the list of task of the current environment
        Params:
        name: the name of the task
        Desciption: short description of task
        """
        task = Task(parent= self._parentEnvironment, name = name, description = description, status = status)
        #yield task.setup()
        self._tasks[task.cid] = task
        yield self._persistenceLayer.save_task(task)
        log.msg("Added task named:",name ," description:",description,"with id",task.cid, system="task manager", logLevel=logging.CRITICAL)         
        self._signal_dispatcher.send_message("task.created",self,task)
        defer.returnValue(task)
    
    def get_task(self,id):
        """
        returns the task with given id
        """
        if not id in self._tasks.keys():
            raise TaskNotFound() 
        else: 
            defer.succeed(self._tasks[id])
    
    def get_tasks(self,filter=None):
        """
        Returns the list of tasks, filtered by  the filter param
        the filter is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check against
        """
        d=defer.Deferred()
        def filter_check(task,filter):
            for key in filter.keys():
                if not getattr(task, key) in filter[key]:
                    return False
            return True
      
        def get(filter,tasksList):
            if filter:
                return [task for task in tasksList if filter_check(task,filter)]
            else:               
                return tasksList
            
        d.addCallback(get,self._tasks.values())
        reactor.callLater(0.5,d.callback,filter)
        return d
          
    @defer.inlineCallbacks  
    def remove_task(self,id,forceStop=False):
        """Removes the task with id==id 
        Shuts down the task before removing it 
        If forcestop is true, shutdown the task even if it is running
        """
        task = self._tasks[id]
        if forceStop:
            if task.isRunning:
                    task.shutdown()
        yield self._persistenceLayer.delete_task(task) 
        del self._tasks[id]
        self._send_signal("task_deleted", task)
        log.msg("Removed task ",task.name,logLevel=logging.CRITICAL)      
       
    @defer.inlineCallbacks
    def clear_tasks(self,forceStop=False):
        """Clears the task list completely 
        Params: forceStop: if set to true, the current running task gets stopped and removed aswell
        """
        for device in self._tasks.values():
                yield self.remove_task(device.id)  
        self._send_signal("devices_cleared", self._tasks)   
       
    """
    ####################################################################################
    The following are the methods for the more detailed manipulation of tasks
    """ 
    def add_conditionToTask(self, id, condition):
        pass
    
    def add_actionToTask(self, id, action):
        pass