import logging
from twisted.internet import reactor, defer
from twisted.python import log,failure
from pollapli.core.logic.tools.signal_system import SignalHander
from pollapli.core.logic.components.tasks.task import Task
from pollapli.exceptions import TaskNotFound

class TaskManager(object):    
    def __init__(self, parentEnvironment):
        self._parentEnvironment = parentEnvironment
        self._persistenceLayer = parentEnvironment._persistenceLayer
        self._tasks = {}
        self.signalChannel = "task_manager"
        self.signalHandler = SignalHander(self.signalChannel)
        self.signalChannelPrefix = "environment_"+str(self._parentEnvironment._id)
    
    @defer.inlineCallbacks
    def setup(self):    
        if self._persistenceLayer is None:
            self._persistenceLayer = self._parentEnvironment._persistenceLayer        
        tasks = yield self._persistenceLayer.load_tasks()
        for task in tasks:
            task._parent = self._parentEnvironment
            task._persistenceLayer = self._persistenceLayer
            self._tasks[task._id] = task
            #yield device.setup()   
        
    def send_signal(self,signal="",data=None):
        prefix=self.signalChannelPrefix+"."
        self.signalHandler.send_message(prefix+signal,self,data)
    
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of tasks
    """
 
    @defer.inlineCallbacks
    def add_task(self,name="task",description="",params={},*args,**kwargs):
        """
        Add a new task to the list of task of the current environment
        Params:
        name: the name of the task
        Desciption: short description of task
        """
        task = yield Task(name = name,description = description)
        yield task.setup()
        self._persistenceLayer.save_task(task)
        
        self.signalHandler.send_message("task.created",self,task)
        log.msg("Added task named:",name ," description:",description,"with id",task._id, system="task manager", logLevel=logging.CRITICAL)         
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
        self.send_signal("task_deleted", task)
        log.msg("Removed task ",task._name,logLevel=logging.CRITICAL)      
       
    @defer.inlineCallbacks
    def clear_tasks(self,forceStop=False):
        """Clears the task list completely 
        Params: forceStop: if set to true, the current running task gets stopped and removed aswell
        """
        for device in self._tasks.values():
                yield self.remove_task(device.id)  
        self.send_signal("devices_cleared", self._tasks)   
        