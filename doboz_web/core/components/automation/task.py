import logging
import time
import datetime
import sys
import os
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure

from louie import dispatcher,error,Any,All
from doboz_web.core.signal_system import SignalHander

class ActionStatus(object):
    def __init__(self,progressIncrement=0,progress=0):
        self.isStarted=False
        self.isPaused=False
        self.progressIncrement=progressIncrement
        self.progress=progress
        self.startTime=0       
        self.totalTime=0
        
    def start(self): 
        self.isStarted=True
        self.isPaused=False
        self.progress=0
        self.startTime=time.time()
            
    def stop(self):
        self.isPaused=True#should it be paused or should is running be set  to false?
        self.isStarted=False
        
    def update_progress(self,value=None,increment=None):
        if value:
            self.progress=value
        elif increment:
            self.progress+=increment
        else:
            self.progress+=self.progressIncrement
            
        self.totalTime=time.time()-self.startTime
        if self.progress==100:
            self.isPaused=True#should it be paused or should is running be set  to false?
            self.isStarted=False
        
    def _toDict(self):
        return {"status":{"isStarted":self.isStarted,"isPaused":self.isPaused,"progress":self.progress,\
                          "progressIncrement":self.progressIncrement,"timeStarted":self.startTime,"timeTotal":self.totalTime}}
 

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