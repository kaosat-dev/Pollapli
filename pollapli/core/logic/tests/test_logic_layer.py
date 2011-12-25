import os, logging, sys
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.logic.logic_layer import LogicLayer
from pollapli.core.logic.components.devices.device import Device
from pollapli.core.logic.components.environments.environment import Environment
from pollapli.exceptions import EnvironmentNotFound
from pollapli.core.persistence.persistence_layer import PersistenceLayer
from pollapli.core.logic.tools.path_manager import PathManager

class LogicLayerTest(unittest.TestCase):   
    @defer.inlineCallbacks 
    def setUp(self):
        self._path_manager = PathManager()
        self._path_manager.dataPath = "."
        self._persistenceLayer = PersistenceLayer(pathManager = self._path_manager)
        self._logicLayer = LogicLayer(self._persistenceLayer)
        yield self._logicLayer.setup()
        
    def tearDown(self):
        self._persistenceLayer.tearDown()
        if os.path.exists("pollapli.db"):
            os.remove("pollapli.db")
        
    @defer.inlineCallbacks
    def test_add_environment(self):
        exp = Environment(name="Test Environment", description="A test Environment", status="active")
        obs =  yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        self.assertEquals(obs.name, exp.name)
        self.assertEquals(obs.description,exp.description)
        self.assertEquals(obs._status,exp._status)
          
        yield self._persistenceLayer.delete_environment(obs)        
        
    @defer.inlineCallbacks
    def test_reload_environments(self):
        environment = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        environment2 = yield self._logicLayer.add_environment(name="Test Environment2", description="A test Environment2", status="inactive")
        
        self._persistenceLayer.tearDown()
        self._persistenceLayer = None
        self._persistenceLayer = PersistenceLayer(pathManager = self._path_manager)
        self._logicLayer = LogicLayer(self._persistenceLayer)
        yield self._logicLayer.setup()
        
        lExpEnvs = [environment,environment2]
        lObsEnvs = yield self._logicLayer.get_environments()
        lObsEnvs = sorted(lObsEnvs,key=lambda environment: environment.name)
        lExpEnvs = sorted(lExpEnvs,key=lambda environment: environment.name)
        self.assertEquals(lObsEnvs,lExpEnvs)
        
        yield self._persistenceLayer.delete_environments([environment,environment2])         
        
    @defer.inlineCallbacks
    def test_remove_environment(self):
        environment = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        yield self._logicLayer.remove_environment(id = environment.cid)
        self.assertRaises(EnvironmentNotFound,self._logicLayer.get_environment,id = environment.cid)
        #self.assertFailure(self._logicLayer.get_environment(id = env.cid) ,EnvironmentNotFound)
       
       
    @defer.inlineCallbacks
    def test_add_devices_to_environment(self):
        environment = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        environment2 = yield self._logicLayer.add_environment(name="Test EnvironmentTwo", description="A test Environment aswell", status="inactive")
        device = yield self._logicLayer.add_device(environmentId = environment.cid, name="Test Device", description = "A test description", type="Test")
        device2 = yield self._logicLayer.add_device(environmentId = environment.cid, name="Test Device Two", description = "Another test description", type="Test")
        device3 = yield self._logicLayer.add_device(environmentId = environment2.cid, name="Test Device Three", type="Test")
        
        lExpDevices = [device,device2]
        lObsDevices = yield self._logicLayer.get_devices(environmentId = environment.cid)
        lExpDevices = sorted(lExpDevices,key=lambda device: device.name)
        lObsDevices = sorted(lObsDevices,key=lambda device: device.name)
        self.assertEquals(lObsDevices,lExpDevices)
        
        lExpDevices = [device3]
        lObsDevices = yield self._logicLayer.get_devices(environmentId = environment2.cid)
        self.assertEquals(lObsDevices,lExpDevices)
        
        yield self._persistenceLayer.delete_environments([environment,environment2])    
        
    @defer.inlineCallbacks
    def test_clear_devices(self):
        
#        logger = logging.getLogger("pollapli.core")
#        logger.setLevel(logging.DEBUG)
#        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#        ch = logging.StreamHandler(sys.stdout)
#        ch.setLevel(logging.DEBUG)
#        ch.setFormatter(formatter)
#        logger.addHandler(ch)
#        observer = log.PythonLoggingObserver("pollapli.core")
#        observer.start()
        
        environment = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        yield environment.add_device(name="Test Device",description = "A test description", type="Test")
        yield environment.add_device(name="Test Device",description = "A test description", type="Test")
    
        devices = yield environment.get_devices()
        self.assertTrue(len(devices)>0)
        
        yield environment.clear_devices()
        devices = yield environment.get_devices()
        self.assertTrue(len(devices)==0)
        
        yield self._persistenceLayer.delete_environment(environment) 
        
    @defer.inlineCallbacks    
    def test_add_tasks_to_environment(self):
        environment = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        environment2 = yield self._logicLayer.add_environment(name="Test EnvironmentTwo", description="A test Environment aswell", status="inactive")
        task = yield self._logicLayer.add_task(environmentId = environment.cid, name="Test Task",description = "A test description")
        task2 = yield self._logicLayer.add_task(environmentId = environment.cid, name="Test Task Two",description = "A test description too")
        task3 = yield self._logicLayer.add_task(environmentId = environment2.cid, name="Test Task Three")
        
        lExpTasks = [task,task2]
        lObsTasks = yield self._logicLayer.get_tasks(environmentId = environment.cid)
        lExpTasks = sorted(lExpTasks,key=lambda task: task.name)
        lObsTasks = sorted(lObsTasks,key=lambda task: task.name)
        self.assertEquals(lObsTasks, lExpTasks)
        
        lExpTasks = [task3]
        lObsTasks = yield self._logicLayer.get_tasks(environmentId = environment2.cid)
        self.assertEquals(lObsTasks, lExpTasks)
        
        yield self._persistenceLayer.delete_environments([environment,environment2]) 
        
    @defer.inlineCallbacks
    def test_reload_tasks(self):
        environment = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        environment2 = yield self._logicLayer.add_environment(name="Test Environment2", description="A test Environment2", status="inactive")
        
        task = yield self._logicLayer.add_task(environmentId = environment.cid, name="Test Task",description = "A test description")
        task2 = yield self._logicLayer.add_task(environmentId = environment.cid, name="Test Task Two",description = "A test description too")
        task3 = yield self._logicLayer.add_task(environmentId = environment2.cid, name="Test Task Three")
        
        self._persistenceLayer.tearDown()
        self._persistenceLayer = None
        self._persistenceLayer = PersistenceLayer(pathManager = self._path_manager)
        self._logicLayer = LogicLayer(self._persistenceLayer)
        yield self._logicLayer.setup()
        
        lExpTasksEnv1 = [task,task2]
        lObsTasksEnv1 = yield self._logicLayer.get_tasks(environmentId = environment.cid)
        lExpTasksEnv1 = sorted(lExpTasksEnv1,key=lambda task: task.name)
        lObsTasksEnv1 = sorted(lObsTasksEnv1,key=lambda task: task.name)
        self.assertEquals(lObsTasksEnv1, lExpTasksEnv1)
        
        lExpTasksEnv2 = [task3]
        lObsTasksEnv2 = yield self._logicLayer.get_tasks(environmentId = environment2.cid)
        lExpTasksEnv2 = sorted(lExpTasksEnv2,key=lambda task: task.name)
        lObsTasksEnv2 = sorted(lObsTasksEnv2,key=lambda task: task.name)
        self.assertEquals(lObsTasksEnv2, lExpTasksEnv2)
        
        yield self._persistenceLayer.delete_environments([environment,environment2]) 
        
    @defer.inlineCallbacks
    def test_reload_devices(self):
        environment = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        environment2 = yield self._logicLayer.add_environment(name="Test Environment2", description="A test Environment2", status="inactive")
        
        device = yield self._logicLayer.add_device(environmentId = environment.cid, name="Test Device",description = "A test description")
        device2 = yield self._logicLayer.add_device(environmentId = environment.cid, name="Test Device Two",description = "A test description too")
        device3 = yield self._logicLayer.add_device(environmentId = environment2.cid, name="Test Device Three")
        
        self._persistenceLayer.tearDown()
        self._persistenceLayer = None
        self._persistenceLayer = PersistenceLayer(pathManager = self._path_manager)
        self._logicLayer = LogicLayer(self._persistenceLayer)
        yield self._logicLayer.setup()
        
        lExpDevicesEnv1 = [device,device2]
        lObsDevicesEnv1 = yield self._logicLayer.get_devices(environmentId = environment.cid)
        lExpDevicesEnv1 = sorted(lExpDevicesEnv1,key=lambda device: device.name)
        lObsDevicesEnv1 = sorted(lObsDevicesEnv1,key=lambda device: device.name)
        self.assertEquals(lObsDevicesEnv1, lExpDevicesEnv1)
        
        lExpDevicesEnv2 = [device3]
        lObsDevicesEnv2 = yield self._logicLayer.get_devices(environmentId = environment2.cid)
        lExpDevicesEnv2 = sorted(lExpDevicesEnv2,key=lambda device: device.name)
        lObsDevicesEnv2 = sorted(lObsDevicesEnv2,key=lambda device: device.name)
        self.assertEquals(lObsDevicesEnv2, lExpDevicesEnv2)
        
        yield self._persistenceLayer.delete_environments([environment,environment2]) 
        
    @defer.inlineCallbacks
    def test_reload_complete(self):
        environment = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        environment2 = yield self._logicLayer.add_environment(name="Test Environment2", description="A test Environment2", status="inactive")
        
        task = yield self._logicLayer.add_task(environmentId = environment.cid, name="Test Task",description = "A test description")
        task2 = yield self._logicLayer.add_task(environmentId = environment.cid, name="Test Task Two",description = "A test description too")
        task3 = yield self._logicLayer.add_task(environmentId = environment2.cid, name="Test Task Three")
        task4 = yield self._logicLayer.add_task(environmentId = environment2.cid, name="Test Task Four")
        
        device = yield self._logicLayer.add_device(environmentId = environment.cid, name="Test Device", description = "A test description", type="Test")
        device2 = yield self._logicLayer.add_device(environmentId = environment2.cid, name="Test Device Two", description = "Another test description", type="Test")
        device3 = yield self._logicLayer.add_device(environmentId = environment2.cid, name="Test Device Three", type="Test")
        
        """destroy current layer, restart and reload"""
        self._persistenceLayer.tearDown()
        self._persistenceLayer = None
        self._persistenceLayer = PersistenceLayer(pathManager = self._path_manager)
        self._logicLayer = LogicLayer(self._persistenceLayer)
        yield self._logicLayer.setup()
        
        lExpEnvs = [environment,environment2]
        lObsEnvs = yield self._logicLayer.get_environments()
        lObsEnvs = sorted(lObsEnvs,key=lambda environment: environment.name)
        lExpEnvs = sorted(lExpEnvs,key=lambda environment: environment.name)
        self.assertEquals(lObsEnvs,lExpEnvs)
        
        lExpTasksEnv1 = [task,task2]
        lObsTasksEnv1 = yield self._logicLayer.get_tasks(environmentId = environment.cid)
        lExpTasksEnv1 = sorted(lExpTasksEnv1,key=lambda task: task.name)
        lObsTasksEnv1 = sorted(lObsTasksEnv1,key=lambda task: task.name)
        self.assertEquals(lObsTasksEnv1, lExpTasksEnv1)
        
        lExpTasksEnv2 = [task3,task4]
        lObsTasksEnv2 = yield self._logicLayer.get_tasks(environmentId = environment2.cid)
        lExpTasksEnv2 = sorted(lExpTasksEnv2,key=lambda task: task.name)
        lObsTasksEnv2 = sorted(lObsTasksEnv2,key=lambda task: task.name)
        self.assertEquals(lObsTasksEnv2, lExpTasksEnv2)
        
        lExpDevicesEnv1 = [device]
        lObsDevicesEnv1 = yield self._logicLayer.get_devices(environmentId = environment.cid)
        lExpDevicesEnv1 = sorted(lExpDevicesEnv1,key=lambda device: device.name)
        lObsDevicesEnv1 = sorted(lObsDevicesEnv1,key=lambda device: device.name)
        self.assertEquals(lObsDevicesEnv1, lExpDevicesEnv1)
        
        lExpDevicesEnv2 = [device2,device3]
        lObsDevicesEnv2 = yield self._logicLayer.get_devices(environmentId = environment2.cid)
        lExpDevicesEnv2 = sorted(lExpDevicesEnv2,key=lambda device: device.name)
        lObsDevicesEnv2 = sorted(lObsDevicesEnv2,key=lambda device: device.name)
        self.assertEquals(lObsDevicesEnv2, lExpDevicesEnv2)
        
        yield self._persistenceLayer.delete_environments([environment,environment2]) 
        
    @defer.inlineCallbacks
    def test_task_schedule(self):
        environment = yield self._logicLayer.add_environment(name="Test Environment", description="A test Environment", status="active")
        task = yield self._logicLayer.add_task(environmentId = environment.cid, name="Test Task",description = "A test description")
#        task.add_action()
#        task.add_condtion()
        
        yield self._persistenceLayer.delete_environment(environment) 
#    test_reload_environments.skip = "disabled temporarly"
#    test_add_environment.skip = "disabled temporarly"
#    test_add_devices_to_environment.skip = "disabled temporarly"
#    test_reload_complete.skip = "disabled temporarly"
#    test_add_tasks_to_environment.skip = "disabled temporarly"
#    test_clear_devices.skip = "disabled temporarly"
        
    
    