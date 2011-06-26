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
from doboz_web.core.tools.event_sys import *


class AutomationEvents(Events):
    __events__=("OnEntered","OnExited","ActionDone")
    

class Task(DBObject):
    BELONGSTO   = ['node','environment']      
    """
    Base class for tasks (printing , scanning etc
    """
    def __init__(self,name="task",description="a task",*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.automation.task")
        #self.logger=logging.getLogger("dobozweb.core.components.automation.task")
       
        self.connector=None
        self.name=name
        self.description=description
        
        self.isRunning=False
            
        self.startTime=time.time()        
        self.totalTime=0#for total print/scan time count
        
        self.progressFraction=0
        self.progress=0
        self.status="NP" #can be : NP: not started, paused , SP: started, paused, SR:started, running

        self.events=AutomationEvents()
        self.startPause()
    def _toDict(self):
        return {"task":{"id":self.id,"name":self.name,"description":self.description,"status":self.status,"link":{"rel":"task"}}}
    
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
    def _toJson(self):
        return '"id":'+ str(self.id)+',"progress":"'+str(self.progress)+'","status":"'+self.status+'"'
    
    def _do_action_step(self):
        """
        do sub action in task
        """
        raise NotImplementedException("This needs to be implemented in a subclass")
