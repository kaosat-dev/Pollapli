from twisted.trial import unittest
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.logic.components.environments.environment_manager import EnvironmentManager
from pollapli.exceptions import EnvironmentNotFound
from pollapli.core.logic.tools.path_manager import PathManager
from pollapli.core.persistence.persistence_layer import PersistenceLayer
import os
from pollapli.core.logic.components.environments.environment import Environment
 
class EnvironmentTest(unittest.TestCase):
    
    @defer.inlineCallbacks
    def setUp(self):
        self._pathManager = PathManager()
        self._pathManager.dataPath = "."
        self._persistenceLayer = PersistenceLayer(pathManager = self._pathManager)
        self.environmentManager=EnvironmentManager(self._persistenceLayer)
        #yield self._persistenceLayer.setup()
        yield self.environmentManager.setup()
        
    def tearDown(self):
        self.environmentManager.teardown()
        self._persistenceLayer.tearDown()
        if os.path.exists("pollapli.db"):
            os.remove("pollapli.db")
    
    @defer.inlineCallbacks
    def test_add_environment(self):
        exp = Environment(name="Test Environment", description="A test Environment", status="active")
        obs =  yield self.environmentManager.add_environment(name="Test Environment", description="A test Environment", status="active")
        self.assertEquals(obs.name, exp.name)
        self.assertEquals(obs.description,exp.description)
        self.assertEquals(obs._status,exp._status)
    
    
    @defer.inlineCallbacks
    def test_get_environmment_byName(self):
        yield self.environmentManager.add_environment(name="Oh my an Environment", description="A test Environment", status="active")
        environment2 =  yield self.environmentManager.add_environment(name="Test Environment", description="A test Environment", status="active")
        exp = environment2
        obs = yield self.environmentManager.get_environments({"name":["Test Environment"]})
        obs  = obs[0]
        self.assertEquals(obs,exp)
    
    @defer.inlineCallbacks
    def test_remove_environment(self):
        environment = yield self.environmentManager.add_environment(name="Test Environment", description="A test Environment", status="active")
        yield self.environmentManager.remove_environment(id = environment._id)
        self.assertRaises(EnvironmentNotFound,self.environmentManager.get_environment,id = environment._id)
        
    @defer.inlineCallbacks
    def test_clear_environments(self):
        yield self.environmentManager.add_environment(name="Test Environment", description="A test Environment", status="active")
        yield self.environmentManager.add_environment(name="Test Environment2", description="A test Environment", status="active")

        yield self.environmentManager.clear_environments()
        obs = yield self.environmentManager.get_environments()
        exp = []
        self.assertEquals(obs,exp)
        