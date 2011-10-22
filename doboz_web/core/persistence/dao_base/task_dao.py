import abc

class TaskDao(object):
    __metaclass__ = abc.ABCMeta
     
    @abc.abstractmethod
    def load_task(self,*args,**kwargs):
        """Retrieve data from task object."""
        return
    
    @abc.abstractmethod
    def load_tasks(self,*args,**kwargs):
        """Retrieve multiple task objects."""
        return
    
    @abc.abstractmethod
    def save_task(self, task):
        """Save the task object ."""
        return
    
   
    