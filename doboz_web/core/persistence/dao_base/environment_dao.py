import abc

class EnvironmentDao(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def create_environment(self,*args,**kwargs):
        """create update object."""
        return
    
    @abc.abstractmethod
    def load_environment(self,*args,**kwargs):
        """Retrieve data from update object."""
        return
    
    @abc.abstractmethod
    def load_environments(self,*args,**kwargs):
        """Retrieve multiple environment objects."""
        return
    
    @abc.abstractmethod
    def save_environment(self, environment):
        """Save the environment object ."""
        return