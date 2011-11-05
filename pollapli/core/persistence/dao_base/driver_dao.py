import abc 

class DriverDao(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def load_driver(self,id = None, *args,**kwargs):
        """Retrieve data for driver object."""
        return
    
    @abc.abstractmethod
    def load_drivers(self,*args,**kwargs):
        """Retrieve data for all driver object."""
        return
    
    @abc.abstractmethod
    def save_driver(self, driver):
        """Save the driver object ."""
        return
    
    @abc.abstractmethod
    def save_drivers(self, lDevices):
        """Save a list of driver object ."""
        return