"""
.. py:module:: task_manager
   :synopsis: main manager of tasks (automation).
"""

import logging
import time
import datetime
import uuid

from doboz_web.core.components.automation.print_task import PrintTask
from doboz_web.core.components.automation.timer_task import TimerTask
 

class TaskManager(object):
    taskTypes={}
    taskTypes["print"]=PrintTask
    taskTypes["timer"]=TimerTask
    
    def __init__(self,connector=None):
        self.logger=logging.getLogger("dobozweb.core.components.automation.taskManager")
        self.tasks=[]
        self.connector=connector
        
#    def __getattr__(self, attr_name):
#        if hasattr(self.tasksById[id], attr_name):
#                return getattr(self.tasksById, attr_name)
#        else:
#            raise AttributeError(attr_name)
        
    def add_task(self,name,type,*args,**kwargs):
        """
        Adds the task to the tasklist
        TODO add weakref to task
        """
        task=None
        if type in TaskManager.taskTypes.iterkeys():
            task=TaskManager.taskTypes[type](**kwargs)
            self.tasks.append(task)
            id=self.tasks.index(task)
            self.tasks[id].id=id
            task.events.OnExited+=self._on_task_exited
            self.logger.critical("Added  task %s of type %s with id set to %s",name,type,str(task.id))
            #self.logger.critical ("Task %s added , %d remaining tasks before starting",task.id,len(self.tasks)-1)        
        else:
            self.logger.critical("unknown task type")
        #task.id=str(uuid.uuid4()) 
        return task
            
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
        print("getting task")
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
        
    