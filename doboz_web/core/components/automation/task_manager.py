"""
.. py:module:: task_manager
   :synopsis: main manager of tasks (automation).
"""

import logging
import time
import datetime
import uuid
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from doboz_web.core.components.automation.print_task import PrintTask
#from doboz_web.core.components.automation.timer_task import TimerTask
from doboz_web.core.components.automation.task import Task
from doboz_web.core.tools.wrapper_list import WrapperList


class TaskManager(object):
    taskTypes={}
    taskTypes["print"]=PrintTask
 #   taskTypes["timer"]=TimerTask
    taskTypes["task"]=Task
    
    def __init__(self,parentNode):
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.automation.taskmanager")
        self.tasks={}
        self.parentNode=parentNode
        self.connector=parentNode.connector
        
#    def __getattr__(self, attr_name):
#        if hasattr(self.tasksById[id], attr_name):
#                return getattr(self.tasksById, attr_name)
#        else:
#            raise AttributeError(attr_name)
    
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of tasks
    """
    
    @defer.inlineCallbacks
    def add_task(self,name="task",description="",type=None,params={},*args,**kwargs):
        """
        Add a new node to the list of nodes of the current environment
        Params:
        name: the name of the node
        Desciption: short description of node
        type: the type of the node : very important , as it will be used to instanciate the correct class
        instance
        Connector:the connector to use for this node
        Driver: the driver to use for this node's connector
        """
            
        if type in self.taskTypes.iterkeys():
            print("type",type,"params",params)
            task= yield Task(name,description,type,params).save()
            task.specialty=TaskManager.taskTypes[type](**params)
            #task= yield TaskManager.taskTypes[type](name,description,**taskParams).save()
            print("added task",task, "with specialty",task.specialty)
            task.node.set(self.parentNode)         
            def getEnv(env,task):
                task.environment.set(env)
            self.parentNode.environment.get().addCallback(getEnv,task)
            
            task.start()
            self.tasks[task.id]=task
            
            print("tasks",self.tasks)
#            capability= yield NodeManager.nodeTypes[type](name,description).save()
#            capability.environment.set(self.parentEnv)
#            capability.node.set(node)
#            node.capability=capability
            #task.events.OnExited+=self._on_task_exited
            log.msg("Added  task ",name," of type ",type," with id set to ",str(task.id), logLevel=logging.CRITICAL)
            defer.returnValue(task)
        else:
            log.msg("unknown node type",logLevel=logging.CRITICAL)
            raise(UnknownNodeType())
        defer.returnValue(None)
        
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
            print("taskList",tasksList)
            if filter:
                
                return WrapperList(data=[task for task in nodesList if filter_check(task,filter)],rootType="tasks")
            else:               
                return WrapperList(data=tasksList,rootType="tasks")
            
        d.addCallback(get,self.tasks.values())
        reactor.callLater(0.5,d.callback,filter)
        return d
            
    def remove_task(self,id,forceStop=False):
        """Removes the task with id==id 
        Shuts down the task before removing it 
        If forcestop is true, shutdown the task even if it is running
        """
        if forceStop:
            if self.tasks[id].isRunning:
                    self.tasks[id].shutdown()
        del self.tasks[id]
        self.logger.critical ("Task %s Removed ",id)         
       
    def clear_tasks(self,forceStop=False):
        """Clears the task list completely 
        Params: forceStop: if set to true, the current running task gets stopped and removed aswell
        """
        [self.remove_task(task.id, forceStop) for task in self.tasks]
    
    def get_task(self,id):
        """
        returns the task with given id
        """
        return self.tasks[id]
    
    def start_task(self,id):
        """Starts the task in line"""
        try:
            self.logger.critical ("Starting task with id %d",id)
            self.tasks[id].connect(self.connector)
            self.tasks[id].start()
        except Exception as inst:
            self.logger.critical ("Error while starting task %s",str(inst))
   
    def stop_task(self,id):
        """Forcefully Stops the task with the given id """
        if self.tasks[id].isRunning:
            self.tasks[id].shutdown()
                
    def _on_task_exited(self,args,kargs):
        """Handles the event when the task exited (whether force stopped or because it was finished """
        self._task_shutdown()
        self.logger.critical ("Task Finished ,%g remaining tasks",len(self.tasks))
        
    def _task_shutdown(self):
        """helper function for cleaning up after a task ended """
        self.currentTask.disconnect()
        self.currentTask.events.OnExited-=self._on_task_exited
        self.currentTask=None 
        del self.tasks[0]   
        
    