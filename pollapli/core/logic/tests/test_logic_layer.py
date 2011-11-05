import os, logging, sys
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.logic.logic_layer import LogicLayer
from pollapli.core.logic.components.devices.device import Device
from pollapli.core.logic.components.updates.update import Update
from pollapli.core.logic.components.environments.environment import Environment
from pollapli.exceptions import EnvironmentNotFound
from pollapli.core.persistence.persistence_layer import PersistenceLayer
import time

class LogicLayerTest(unittest.TestCase):   
    @defer.inlineCallbacks 
    def setUp(self):
        self._persistenceLayer = PersistenceLayer()
        self._logicLayer = LogicLayer(self._persistenceLayer)
        yield self._logicLayer.setup()
        
    def tearDown(self):
        self._persistenceLayer.tearDown()
        if os.path.exists("pollapli.db"):
            os.remove("pollapli.db")
        
#    @defer.inlineCallbacks
#    def test_add_environment(self):
#        exp = Environment(name="Test Environment", description="A test Environment", status="active")
#        obs =  yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
#        self.assertEquals(obs._name, exp._name)
#        self.assertEquals(obs._description,exp._description)
#        self.assertEquals(obs._status,exp._status)
#        
#        
#    @defer.inlineCallbacks
#    def test_reload_environments(self):
#        environment = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
#        environment2 = yield self._logicLayer.add_environment(name="Test Environment2", description="A test Environment2", status="inactive")
#        
#        self._persistenceLayer.tearDown()
#        self._persistenceLayer = None
#        self._persistenceLayer = PersistenceLayer()
#        self._logicLayer = LogicLayer(self._persistenceLayer)
#        yield self._logicLayer.setup()
#        
#        lExpEnvs = [environment,environment2]
#        lObsEnvs = yield self._logicLayer.get_environments()
#        self.assertEquals(sorted(lObsEnvs),sorted(lExpEnvs))
#         
#    @defer.inlineCallbacks
#    def test_remove_environment(self):
#        env = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
#        yield self._logicLayer.remove_environment(id = env._id)
##        obs =  self._logicLayer.get_environment(id = env._id)
##        print("obs",obs)
#        self.assertRaises(self._logicLayer.get_environment(id = env._id) ,EnvironmentNotFound)
#        #self.assertFailure(self._logicLayer.get_environment(id = env._id) ,EnvironmentNotFound)
#    
#    @defer.inlineCallbacks
#    def test_add_device_to_environment(self):
#        #FIXME: should the adding of devices not go through an environment ? :ie getting a specific environment, then
#        #adding the device to it feels clunky  and should be something like : add_device(envId, bla bla)
#        env = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
#        device = yield env.add_device(name="Test Device",description = "A test description", type="Test")
#    
#        lExpDevices = [device]
#        lObsDevices = yield env.get_devices()
#        self.assertEquals(lObsDevices,lExpDevices)
#        
    @defer.inlineCallbacks
    def test_clear_devices(self):
        
        logger = logging.getLogger("pollapli.core")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        observer = log.PythonLoggingObserver("pollapli.core")
        observer.start()
        
        env = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        yield env.add_device(name="Test Device",description = "A test description", type="Test")
        yield env.add_device(name="Test Device",description = "A test description", type="Test")
    
        devices = yield env.get_devices()
        self.assertTrue(len(devices)>0)
        
        yield env.clear_devices()
        devices = yield env.get_devices()
        print("devices",devices)
        self.assertTrue(len(devices)==0)
        
    @defer.inlineCallbacks    
    def test_add_task_to_environment(self):
        #FIXME: should the adding of devices not go through an environment ? :ie getting a specific environment, then
        #adding the device to it feels clunky  and should be something like : add_device(envId, bla bla)
        env = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        task = yield env.add_task(name="Test Task",description = "A test description")
    
        lExpDevices = [task]
        lObsDevices = yield env.get_tasks()
        self.assertEquals(lObsDevices,lExpDevices)
        
#    def test_task_schedule(self):
#        pass