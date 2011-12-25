from twisted.trial import unittest
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.logic.components.environments.environment_manager import EnvironmentManager
from pollapli.exceptions import EnvironmentNotFound
from pollapli.core.logic.tools.path_manager import PathManager
from pollapli.core.persistence.persistence_layer import PersistenceLayer
import os
from pollapli.core.logic.components.devices.device_manager import DeviceManager
 
class Test_device_manager(unittest.TestCase):
    
    @defer.inlineCallbacks
    def setUp(self):
        self._path_manager = PathManager()
        self._path_manager.dataPath = "."
        self._persistenceLayer = PersistenceLayer(pathManager = self._path_manager)
        self.deviceManager=DeviceManager(self._persistenceLayer)
        #yield self._persistenceLayer.setup()
        yield self.deviceManagers.setup()
        
    def tearDown(self):
        self.deviceManager.teardown()
        self._persistenceLayer.tearDown()
        if os.path.exists("pollapli.db"):
            os.remove("pollapli.db")
    
    
        