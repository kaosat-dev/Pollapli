from twisted.internet import reactor, defer
from pollapli.core.logic.components.environments.environment_manager import EnvironmentManager
from pollapli.core.logic.components.drivers.driver import DriverManager

class LogicLayer(object):
    def __init__(self,persistenceLayer=None):
        self._persistenceLayer = persistenceLayer
        self._environmentManager = EnvironmentManager(self._persistenceLayer)
        #self._driverManager = DriverManager()
    
    @defer.inlineCallbacks
    def setup(self):
        yield self._environmentManager.setup()
        
    def __getattr__(self, attr_name):
        if hasattr(self._environmentManager, attr_name):
            return getattr(self._environmentManager, attr_name)  
        else:
            raise AttributeError(attr_name)
        
        
    def add_task(self,envId,*args,**kwargs):
        self._environmentManager.get_environment(envId).add_task(*args,**kwargs)
        
    def add_device(self,envId,*args,**kwargs):
        self._environmentManager.get_environment(envId).add_device(*args,**kwargs)