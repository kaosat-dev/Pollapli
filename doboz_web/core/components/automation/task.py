"""
.. py:module:: task
   :synopsis: main module of tasks (automation): task , task and action status, task manager etc.
"""
import logging,time,datetime,sys,os,uuid,ast

from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure

from doboz_web.core.components.automation.print_action import PrintAction
from doboz_web.core.components.automation.action import Action
from doboz_web.core.tools.wrapper_list import WrapperList


from doboz_web.core.signal_system import SignalHander



class TaskStatus(object):
    def __init__(self,progressIncrement=0,progress=0):
        self.isStarted=False
        self.isPaused=False
        self.progressIncrement=progressIncrement
        self.progress=progress
        self.startTime=0       
        self.totalTime=0
        
    def update_progress(self,value=None,increment=None):
        if value:
            self.progress=value
        elif increment:
            self.progress+=increment
        else:
            self.progress+=self.progressIncrement
        
    def _toDict(self):
        return {"status":{"isStarted":self.isStarted,"isPaused":self.isPaused,"progress":self.progress,\
                          "progressIncrement":self.progressIncrement,"timeStarted":self.startTime,"timeTotal":self.totalTime}}
 
    
class Task(DBObject):
    BELONGSTO   = ['node']      
    """
    Base class for tasks (printing , scanning etc
    """
    def __init__(self,name="task",description="a task",taskType="task",options={},*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.logger=logging.getLogger("dobozweb.core.components.automation.task")
        
        self.name=name
        self.description=description
        self.taskType=taskType
        self.params=options
        
        """progress need to be computed base on the number of actions needed for this task to complete"""
        self.status=TaskStatus()
        self.actions=None
        self.signalHandler=None
        #self.signalhandler=SignalHander("task",[("driver.dataRecieved",Any,[self.__call__])])

    def __call__(self,*args,**kwargs):
        pass
        
    def _toDict(self):
        return {"task":{"id":self.id,"name":self.name,"description":self.description,"status":self.status._toDict(),"link":{"rel":"task"}}}
    
    @defer.inlineCallbacks  
    def setup(self):
        self.signalChannelPrefix=str((yield self.node.get()).id)
        self.signalChannel="node"+self.signalChannelPrefix+".task"+str(self.id)
        self.driverChannel="node"+self.signalChannelPrefix+".driver"
        self.signalHandler=SignalHander(self.signalChannel)
        log.msg("Task setup sucessfully",system="Task",logLevel=logging.CRITICAL) 
    
    @defer.inlineCallbacks 
    def start(self):
        if self.actions:
            yield self.actions.start()  
            defer.returnValue(True)
        else:
            defer.returnValue(False)  
            
    @defer.inlineCallbacks       
    def pause(self):
        if self.actions:
            yield self.actions.pause()  
            defer.returnValue(True)
        else:
            defer.returnValue(False)
    
    @defer.inlineCallbacks
    def stop(self):
        if self.actions:
            yield self.actions.stop()  
            defer.returnValue(True)
        else:
            defer.returnValue(False)  
    
    def send_signal(self,signal="",data=None,out=False):
        self.signalHandler.send_message(signal,{"data":data},out)
   
    def set_action(self,action):
        """Sets the first action"""
        self.actions=action
        #self.signalHandler.add_handler2(handler=self.actions._data_recieved,signal=self.driverChannel+".dataRecieved")
        self.signalHandler.add_handler(handler=self.actions._data_recieved,signal="dataRecieved")
        
    def check_conditions(self):
        """
        method in charge of verifying all of the tasks conditions
        for a task to start/continue running, all of its conditions must evaluate to True 
        """
        [condtion.check() for condition in self.conditions]
        



class TaskManager(object):
    
    def __init__(self,parentNode):
        self.tasks={}
        self.parentNode=parentNode
        self.connector=parentNode.driver
    
    @defer.inlineCallbacks
    def setup(self):         
        yield self.load(self.parentNode)
        defer.returnValue(None)
        
    
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of tasks
    """
    
    @defer.inlineCallbacks
    def create(parentNode=None,taskType=None,taskParams={},*args,**kwargs):     
        task=None
        if taskType:
            plugins= (yield AddOnManager.get_plugins(idoboz_web.ITask))
            for taskKlass in plugins:
                if taskType==taskKlass.__name__.lower():
                    task=yield Task(taskType=taskType,options=taskParams).save()
                    yield task.save()  
                    task.node.set(parentNode)
                    yield task.setup()
                    break
        else:
            task=yield Task(taskType=taskType,options=taskParams).save()
        if not task:
            raise UnknownTask()
        defer.returnValue(task)
        
    @defer.inlineCallbacks
    def load(self,parentNode=None,taskId=None,taskType=None,*args,**kwargs):
        if taskId is not None:
            """For retrieval of single task"""
            task=yield Task.find(where=['node_id = ? and task_id=?', parentNode.id,taskId])
            defer.returnValue(task)
        else:
            tasks=yield Task.find(where=['node_id = ?', parentNode.id])
            for task in tasks:
                task.node.set(parentNode) 
                yield task.setup()
                #temp hack           
                actions=yield PrintAction.find(where=['task_id = ?', task.id])              
                action=actions[0]
                
                actionParams=ast.literal_eval(action.params)
                action.setup(actionParams)
                
                action.task.set(task)
                action.parentTask=task
                task.set_action(action)
                #print("action info ptask",action.parentTask,"filename",action.printFileName)
                self.tasks[task.id]=task
                
            
                
            defer.returnValue(tasks)
    
    @defer.inlineCallbacks
    def add_task(self,name="task",description="",taskType=None,params={},*args,**kwargs):
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
                
        task= yield Task(name,description,type,params).save()
        task.node.set(self.parentNode)  
        yield task.setup()
        
        action=yield PrintAction(parentTask=task,**params).save()
        action.task.set(task)
        task.set_action(action)
        self.tasks[task.id]=task
        task.start()
            
        print("tasks",self.tasks)
#            capability= yield NodeManager.nodeTypes[type](name,description).save()
#            capability.environment.set(self.parentEnv)
#            capability.node.set(node)
#            node.capability=capability
            #task.events.OnExited+=self._on_task_exited
        log.msg("Added  task ",name," of type ",type," with id set to ",str(task.id), logLevel=logging.CRITICAL)
        defer.returnValue(task)

        
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
        
   