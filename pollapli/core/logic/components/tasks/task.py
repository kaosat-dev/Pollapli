"""
.. py:module:: task
   :synopsis: main module of tasks (automation): task , task and action status, task manager etc.
"""
from pollapli.core.logic.components.base_component import BaseComponent

class Task(BaseComponent):
  
    """
    Base class for tasks
    """
    def __init__(self, parent=None, name="Default Task", description="Default task description",*args,**kwargs):
        BaseComponent.__init__(self, parent)
        self.name=name
        self.description=description    
        """progress need to be computed base on the number of actions needed for this task to complete"""
        #self.status=TaskStatus()
           
    def setup(self):
        pass