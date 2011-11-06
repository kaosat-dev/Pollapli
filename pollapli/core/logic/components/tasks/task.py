"""
.. py:module:: task
   :synopsis: main module of tasks (automation): task , task and action status, task manager etc.
"""
from pollapli.core.logic.components.base_component import BaseComponent

class Task(BaseComponent):
  
    """
    Base class for tasks
    """
    def __init__(self, parent=None, name="Default Task", description="Default task description",status ="inactive",*args,**kwargs):
        BaseComponent.__init__(self, parent)
        self._name = name
        self._description =  description  
        self._status = status 
        """progress need to be computed base on the number of actions needed for this task to complete"""
        #self.status=TaskStatus()
    def __eq__(self, other):
        return self._id == other._id and self._name == other._name and self._description == other._description and self._status == other._status
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def setup(self):
        pass
    
    def add_action(self):
        pass
    
    def add_condition(self):
        pass