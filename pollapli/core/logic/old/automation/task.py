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



from pollapli.core.logic.components.automation.print_action import PrintAction
from pollapli.core.logic.components.automation.action import Action
from pollapli.core.logic.tools.wrapper_list import WrapperList
from pollapli.core.logic.tools.signal_system import SignalHander



class TaskStatus(object):
    def __init__(self,progress_increment=0,progress=0):
        self.is_started=False
        self.is_paused=False
        self.progress_increment=progress_increment
        self.progress=progress
        self.start_time=0       
        self.total_time=0
        
    def update_progress(self,value=None,increment=None):
        if value:
            self.progress=value
        elif increment:
            self.progress+=increment
        else:
            self.progress+=self.progress_increment
        
    def _toDict(self):
        return {"status":{"is_started":self.is_started,"is_paused":self.is_paused,"progress":self.progress,\
                          "progress_increment":self.progress_increment,"timeStarted":self.start_time,"timeTotal":self.total_time}}
 

class Action(object):
    def __init__(self):
        self.steps=0
        self.start_time=time.time()
        
    def do_step(self):
        pass
    
    def resultCallback(self,result):
        """we get any results from our target back through here """
       # print("Action GOT RESULT",result)
        self.steps+=1
        #print("here")
        if self.steps%1000==0:
                log.msg("1000 steps done in",time.time()-self.start_time,"s",logLevel=logging.CRITICAL)
                self.start_time=time.time()
        
        self.do_step()
    
    def start(self):
        log.msg("starting action")
        self.start_time=time.time()
        self.do_step()
   

         
class UpdateAndGetVariable_action(Action):
    def __init__(self,targetNode,targetVariable):
        Action.__init__(self)
        self.targetNode=targetNode
        self.targetVariable=targetVariable
        
    def do_step(self):

        print("self.targetVariable",self.targetVariable)
        self.targetVariable.get(True,self).addCallback(self.resultCallback)
        cmd={"type":0,"target":"test","sender":self}
        self.targetNode.add_command(cmd)

    
class Task(DBObject):
    BELONGSTO   = ['environment']    
    EXPOSE=["name","description","id","type","status","driver"]  
    """
    Base class for tasks
    """
    def __init__(self,name="task",description="a task",taskType="task",options={},*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.name=name
        self.description=description
        
        """progress need to be computed base on the number of actions needed for this task to complete"""
        self.status=TaskStatus()
    
        self.actions=None
        
    def add_action(self,action):
        self.actions=action
        
    def setup(self):
        pass
    def start(self):
        self.actions.start()
    

        



class TaskManager(object):
    
    def __init__(self,parentEnvironment):
        self.tasks={}
        self.parentEnvironment=parentEnvironment
        self._signal_channel="task_manager"
        self.signalHandler=SignalHander(self._signal_channel)
    
    @defer.inlineCallbacks
    def setup(self):         
        yield self.load(self.parentEnvironment)
        self.signal_channel_prefix="environment_"+str(self.parentEnvironment.id)    
        defer.returnValue(self)
    
    def _send_signal(self,signal="",data=None):
        prefix=self.signal_channel_prefix+"."
        self.signalHandler.send_message(prefix+signal,self,data)
    
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of tasks
    """
    
 
    @defer.inlineCallbacks
    def load(self,parentEnvironment=None,taskId=None,taskType=None,*args,**kwargs):
        if taskId is not None:
            """For retrieval of single task"""
            task=yield Task.find(where=['environment_id = ? and task_id=?', parentEnvironment.id,taskId])
            defer.returnValue(task)
        else:
            tasks=yield Task.find(where=['environment_id = ?', parentEnvironment.id])
#            for task in tasks:
#                task.environment.set(parentEnvironment) 
#                yield task.setup()
#                #temp hack           
#                actions=yield PrintAction.find(where=['task_id = ?', task.id])              
#                action=actions[0]
#                
#                actionParams=ast.literal_eval(action.params)
#                action.setup(actionParams)
#                
#                action.task.set(task)
#                action.parentTask=task
#                task.set_action(action)
#                #print("action info ptask",action.parentTask,"filename",action.printFileName)
#                self.tasks[task.id]=task
                
            
                
            defer.returnValue(tasks)
    
    @defer.inlineCallbacks
    def add_task(self,nodeId=None,nodeElement=None,name="task",description="",taskType=None,params={},*args,**kwargs):
        """
        Add a new task to the list of task of the current environment
        Params:
        name: the name of the task
        Desciption: short description of task
        type: the type of the task : very important , as it will be used to instanciate the correct class
        instance
        Connector:the connector to use for this taks
       
        """
        
        """JUST FOR TESTING !!!!
        The finding of nodes and target variables should be done using the normal element.get_subelement(params) API
        """    
        
        targetNode= yield self.parentEnvironment.get_node(1)
        targetVariable=targetNode.testElement
        print("zerzer",targetVariable)
        
        
        task=yield Task(taskType=taskType,extra_params=None).save()
        log.msg("Added  task ",name, logLevel=logging.CRITICAL)
        
        task.add_action(UpdateAndGetVariable_action(targetNode,targetVariable))
        print("Added test action")
        
        task.start()
                
#        task= yield Task(name,description,type,params).save()
#        task.environment.set(self.parentEnvironment)  
#        yield task.setup()
#        
#        action=yield PrintAction(parentTask=task,**params).save()
#        action.task.set(task)
#        task.set_action(action)
#        self.tasks[task.id]=task
#        task.start()
#            
#        print("tasks",self.tasks)
##            capability= yield NodeManager.environmentTypes[type](name,description).save()
##            capability.environment.set(self.parentEnv)
##            capability.environment.set(environment)
##            environment.capability=capability
#            #task.events.OnExited+=self._on_task_exited
#        log.msg("Added  task ",name," of type ",type," with id set to ",str(task.id), logLevel=logging.CRITICAL)
#        defer.returnValue(task)

        
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
                
                return WrapperList(data=[task for task in environmentsList if filter_check(task,filter)],rootType="tasks")
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
        
   