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
        
    @defer.inlineCallbacks
    def add_task(self,environmentId,*args,**kwargs):
        env = self._environmentManager.get_environment(environmentId, *args, **kwargs)
        task = yield env.add_task(*args,**kwargs)
        defer.returnValue(task)
    
    @defer.inlineCallbacks
    def get_tasks(self, environmentId = None, *args, **kwargs):
        env = self._environmentManager.get_environment(environmentId, *args, **kwargs)
        tasks = yield env.get_tasks(*args, **kwargs)
        defer.returnValue(tasks)
     
    @defer.inlineCallbacks   
    def add_device(self,environmentId,*args,**kwargs):
        env = self._environmentManager.get_environment(environmentId)
        device = yield env.add_device(*args,**kwargs)
        defer.returnValue(device)
        
    @defer.inlineCallbacks
    def get_devices(self, environmentId = None, *args, **kwargs):
        env = self._environmentManager.get_environment(environmentId, *args, **kwargs)
        devices = yield env.get_devices(*args, **kwargs)
        defer.returnValue(devices)