import abc

class UpdateDao(object):
    __metaclass__ = abc.ABCMeta
     
    @abc.abstractmethod
    def load_update(self,*args,**kwargs):
        """Retrieve data from update object."""
        return
    
    @abc.abstractmethod
    def load_updates(self,*args,**kwargs):
        """Retrieve multiple update objects."""
        return
    
    @abc.abstractmethod
    def save_update(self, update):
        """Save the update object ."""
        return
    
   
    