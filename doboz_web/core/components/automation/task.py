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
from doboz_web.core.tools.event_sys import *
from doboz_web.core.signal_system import SignalHander


class TaskStatus(object):
    def __init__(self):
        self.isStarted=False
        self.isPaused=False
    
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
        self.params=params
        self.startTime=time.time()        
        self.totalTime=0#for total print/scan time count
        
        self.progressFraction=0
        self.progress=0
        self.status=TaskStatus()
        self.actions=None
        self.signalhandler=SignalHander("task",[("driver.dataRecieved",Any,[self.__call__])])

    def __call__(self):
        print("task recieved message from driver")
        
    def _toDict(self):
        return {"task":{"id":self.id,"name":self.name,"description":self.description,"status":"","progress":self.progress,"link":{"rel":"task"}}}
    
    @defer.inlineCallbacks  
    def setup(self):
        self.signalChannelPrefix=str((yield self.node.get()).id)
        self.signalChannel="node"+self.signalChannelPrefix+".task"+str(self.id)
        self.signalHandler=SignalHander(self.signalChannel,[(All,self.signalChannel,[self.__call__])])
        log.msg("Driver setup sucessfully",system="Driver")  
          
    def start(self):
        if self.actions:
            self.actions.start()
            
    def pause(self):
        pass
    def stop(self):
        pass

    def check_conditions(self):
        """
        method in charge of verifying all of the tasks conditions
        for a task to start/continue running, all of its conditions must evaluate to True 
        """
        [condtion.check() for condition in self.conditions]