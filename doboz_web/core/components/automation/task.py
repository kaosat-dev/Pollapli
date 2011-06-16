import logging
import time
import datetime
import sys
import os


from doboz_web.core.tools.event_sys import *


class AutomationEvents(Events):
    __events__=("OnEntered","OnExited","ActionDone")
    

class Task(object):
    """
    Base class for tasks (printing , scanning etc
    """
    print("jhkhkjh")
    def __init__(self,name="task"):
        self.logger=logging.getLogger("dobozweb.core.components.automation.task")
       
        self.connector=None
        self.name=name
        
        self.isRunning=False
            
        self.startTime=time.time()        
        self.totalTime=0#for total print/scan time count
        
        self.progressFraction=0
        self.progress=0
        self.status="NP" #can be : NP: not started, paused , SP: started, paused, SR:started, running
        self.id=-1
        
        self.events=AutomationEvents()
    
    def startPause(self):
        """
        Switches between active and inactive mode, or starts the task if not already done so
        """
        if self.status=="SR":
            self.status="SP"
            self.logger.critical("Pausing")   
            #update elapsed time
            self.totalTime+=time.time()-self.startTime
        elif self.status=="SP":
            self.status="SR"
            self.logger.critical("Un Pausing")
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
