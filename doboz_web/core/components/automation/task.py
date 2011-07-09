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


class AutomationEvents(Events):
    __events__=("OnEntered","OnExited","ActionDone")
    

class Task(DBObject):
    BELONGSTO   = ['node']      
    """
    Base class for tasks (printing , scanning etc
    """
    def __init__(self,name="task",description="a task",type="task",params={},*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        #self.logger=log.PythonLoggingObserver("dobozweb.core.components.automation.task")
        self.logger=logging.getLogger("dobozweb.core.components.automation.task")
        self.connector=None
        self.name=name
        self.description=description
        self.type=type
        self.isRunning=False
        self.params=params
        self.startTime=time.time()        
        self.totalTime=0#for total print/scan time count
        
        self.progressFraction=0
        self.progress=0
        self.status="NP" #can be : NP: not started, paused , SP: started, paused, SR:started, running

        self.signalhandler=SignalHander("task",[("driver.dataRecieved",Any,[self.__call__])])

    def __call__(self):
        print("task recieved message from driver")
        
    def _toDict(self):
        return {"task":{"id":self.id,"name":self.name,"description":self.description,"status":self.status,"progress":self.progress,"link":{"rel":"task"}}}
    
    def start(self):
        if hasattr(self,"specialty"):
            self.specialty.start()
    def pause(self):
        pass
    def stop(self):
        pass
    
    def startPause(self):
        """
        Switches between active and inactive mode, or starts the task if not already done so
        """
        if self.status=="SR":
            self.status="SP"
            log.msg("Pausing task ",self.id, logLevel=logging.CRITICAL)
            #update elapsed time
            self.totalTime+=time.time()-self.startTime
        elif self.status=="SP":
            self.status="SR"
            log.msg("Unpausing task ",self.id, logLevel=logging.CRITICAL)
            self.startTime=time.time()   
            self._do_action_step()
            
    def enter(self):
        """
        When taks is entered
        """
        self.events.OnEntered(self,"Entered")
        
    def exit(self):
        """
        When taks is exited
        """
        self.events.OnExited(self,"Exited")
 
    def _do_action(self):
        """
        do sub action in task
        """
        raise NotImplementedException("This needs to be implemented in a subclass")

    def check_conditions(self):
        """
        method in charge of verifying all of the tasks conditions
        for a task to start/continue running, all of its conditions must evaluate to True 
        """
        [condtion.check() for condition in self.conditions]