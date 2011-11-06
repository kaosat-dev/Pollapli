import os
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from pollapli.core.persistence.persistence_layer import PersistenceLayer
from pollapli.core.logic.components.devices.device import Device
from pollapli.core.logic.components.updates.update import Update
from pollapli.core.logic.components.environments.environment import Environment
from pollapli.exceptions import DeviceNotFound,EnvironmentNotFound, TaskNotFound
from pollapli.core.logic.components.tasks.task import Task
from pollapli.core.logic.tools.path_manager import PathManager

class PersistenceLayerTest(unittest.TestCase):    
    def setUp(self):
        self._pathManager = PathManager()
        self._pathManager.dataPath = "."
        self._persistenceLayer = PersistenceLayer(pathManager = self._pathManager)
        
    def tearDown(self):
        self._persistenceLayer.tearDown()
        if os.path.exists('pollapli.db'):
            os.remove('pollapli.db')
        
    @defer.inlineCallbacks
    def test_save_and_load_environment(self):
        input = Environment(name="TestEnvironment",description = "A test description")
        yield self._persistenceLayer.save_environment(input)
        exp = input 
        obs = yield self._persistenceLayer.load_environment(id = input._id)
        self.assertEquals(obs,exp)
        
        yield self._persistenceLayer.delete_environment(input)
        
    @defer.inlineCallbacks
    def test_save_and_load_environments(self):
        input =[]
        input.append(Environment(name="TestEnvironmentOne",description = "A test description"))
        input.append(Environment(name="TestEnvironmentTwo",description = "Another test description",status="active"))
       
        yield self._persistenceLayer.save_environments(input)
        exp = input 
        obs =  yield self._persistenceLayer.load_environments()
        self.assertEquals(obs,exp)
        
        yield self._persistenceLayer.delete_environment(input[0])
        yield self._persistenceLayer.delete_environment(input[1])
     
    @defer.inlineCallbacks
    def test_update_environment(self):
        input = Environment(name="TestEnvironment",description = "A test description")
        yield self._persistenceLayer.save_environment(input)
        input.name = "TestEnvironmentModified"
        yield self._persistenceLayer.save_environment(input)
    
        exp = input
        obs = yield self._persistenceLayer.load_environment(id = input._id)
        self.assertEquals(obs,exp)
        yield self._persistenceLayer.delete_environment(input)
    
    @defer.inlineCallbacks
    def test_delete_environment(self):
        input = Environment(name="TestEnvironment",description = "A test description")
        yield self._persistenceLayer.save_environment(input)
        exp = input 
        obs = yield self._persistenceLayer.load_environment(id = input._id)
        self.assertEquals(obs,exp)
        
        yield self._persistenceLayer.delete_environment(input)
        obs = self._persistenceLayer.load_environment(id = input._id)
        self.assertFailure(obs ,EnvironmentNotFound )
    
    def test_delete_environment_exception(self):
        input = Environment(name="TestEnvironment",description = "A test description")
        obs = self._persistenceLayer.delete_environment(input)
        self.assertFailure(obs ,EnvironmentNotFound )
    
    @defer.inlineCallbacks
    def test_save_and_load_device(self):
        input = Device(name="TestDevice",description = "A test description")
        yield self._persistenceLayer.save_device(input)
        exp = input 
        obs = yield self._persistenceLayer.load_device(id = input._id)
        self.assertEquals(obs,exp)
    
    @defer.inlineCallbacks
    def test_save_and_load_devices(self):
        input =[]
        input.append(Device(name="TestDeviceOne",description = "A test description"))
        input.append(Device(name="TestDeviceTwo",description = "Another test description",status="active"))
       
        yield self._persistenceLayer.save_devices(input)
        exp = input 
        obs =  yield self._persistenceLayer.load_devices()
        self.assertEquals(obs,exp)
          
    @defer.inlineCallbacks
    def test_save_and_load_devices_one_by_one(self):
        input =[]
        input.append(Device(name="TestDeviceOne",description = "A test description"))
        input.append(Device(name="TestDeviceTwo",description = "Another test description",status="active"))
       
        yield self._persistenceLayer.save_device(input[0])
        yield self._persistenceLayer.save_device(input[1])
        exp = input 
        obs =  yield self._persistenceLayer.load_devices()
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_save_and_load_devices_of_environment(self):
        parentEnvironement = Environment(name="TestEnvironment",description = "A test description")
        device1 = Device(name="TestDeviceOne",description = "A test description")
        device1._parent = parentEnvironement
        device2 = Device(name="TestDeviceTwo",description = "Another test description",status="active")
        device2._parent = parentEnvironement
        input =[device1,device2]
        
        parentEnvironement2 = Environment(name="TestEnvironment2",description = "A test description")
        device3 = Device(name="TestDeviceThree",description = "A test description")
        device3._parent = parentEnvironement2

        yield self._persistenceLayer.save_devices(input)
        yield self._persistenceLayer.save_device(device3)
        
        exp = input 
        obs =  yield self._persistenceLayer.load_devices(parentEnvironement._id)
        self.assertEquals(obs,exp)
        
        exp = [device3]
        obs =  yield self._persistenceLayer.load_devices(parentEnvironement2._id)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_update_device(self):
        input = Device(name="TestDevice",description = "A test description")
        yield self._persistenceLayer.save_device(input)
        input.name = "TestDeviceModified"
        yield self._persistenceLayer.save_device(input)
    
        exp = input
        obs = yield self._persistenceLayer.load_device(id = input._id)
        self.assertEquals(obs,exp)      
    
    @defer.inlineCallbacks
    def test_delete_device(self):
        input = Device(name="TestDevice",description = "A test description")
        yield self._persistenceLayer.save_device(input)
        exp = input 
        obs = yield self._persistenceLayer.load_device(id = input._id)
        self.assertEquals(obs,exp)
        
        yield self._persistenceLayer.delete_device(input)
        obs = self._persistenceLayer.load_device(id = input._id)
        self.assertFailure(obs ,DeviceNotFound )
    
    def test_delete_device_exception(self):
        input = Device(name="TestDevice",description = "A test description")
        obs = self._persistenceLayer.delete_device(input)
        self.assertFailure(obs ,DeviceNotFound )
        
    """
    ####################################################################################
    The following are the Task related tests
    """
    
    @defer.inlineCallbacks
    def test_save_and_load_task(self):
        input = Task(name="TestTask",description = "A test description")
        yield self._persistenceLayer.save_task(input)
        exp = input 
        obs = yield self._persistenceLayer.load_task(id = input._id)
        self.assertEquals(obs,exp)
    
    @defer.inlineCallbacks
    def test_save_and_load_tasks(self):
        input =[]
        input.append(Task(name="TestTaskOne",description = "A test description"))
        input.append(Task(name="TestTaskTwo",description = "Another test description",status="active"))
       
        yield self._persistenceLayer.save_tasks(input)
        exp = input 
        obs =  yield self._persistenceLayer.load_tasks()
        self.assertEquals(obs,exp)
          
    @defer.inlineCallbacks
    def test_save_and_load_tasks_one_by_one(self):
        input =[]
        input.append(Task(name="TestTaskOne",description = "A test description"))
        input.append(Task(name="TestTaskTwo",description = "Another test description",status="active"))
       
        yield self._persistenceLayer.save_task(input[0])
        yield self._persistenceLayer.save_task(input[1])
        exp = input 
        obs =  yield self._persistenceLayer.load_tasks()
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_save_and_load_tasks_of_environment(self):
        parentEnvironement = Environment(name="TestEnvironment",description = "A test description")
        task1 = Task(name="TestTaskOne",description = "A test description")
        task1._parent = parentEnvironement
        task2 = Task(name="TestTaskTwo",description = "Another test description",status="active")
        task2._parent = parentEnvironement
        input =[task1,task2]
        
        parentEnvironement2 = Environment(name="TestEnvironment2",description = "A test description")
        task3 = Task(name="TestTaskThree",description = "A test description")
        task3._parent = parentEnvironement2

        yield self._persistenceLayer.save_tasks(input)
        yield self._persistenceLayer.save_task(task3)
        
        exp = input 
        obs =  yield self._persistenceLayer.load_tasks(parentEnvironement._id)
        self.assertEquals(obs,exp)
        
        exp = [task3]
        obs =  yield self._persistenceLayer.load_tasks(parentEnvironement2._id)
        self.assertEquals(obs,exp)
        
    @defer.inlineCallbacks
    def test_update_task(self):
        input = Task(name="TestTask",description = "A test description")
        yield self._persistenceLayer.save_task(input)
        input.name = "TestTaskModified"
        yield self._persistenceLayer.save_task(input)
    
        exp = input
        obs = yield self._persistenceLayer.load_task(id = input._id)
        self.assertEquals(obs,exp)
    
    @defer.inlineCallbacks
    def test_delete_task(self):
        input = Task(name="TestTask",description = "A test description")
        yield self._persistenceLayer.save_task(input)
        exp = input 
        obs = yield self._persistenceLayer.load_task(id = input._id)
        self.assertEquals(obs,exp)
        
        yield self._persistenceLayer.delete_task(input)
        obs = self._persistenceLayer.load_task(id = input._id)
        self.assertFailure(obs ,TaskNotFound )
    
    def test_delete_task_exception(self):
        input = Task(name="TestTask",description = "A test description")
        obs = self._persistenceLayer.delete_task(input)
        self.assertFailure(obs ,TaskNotFound )
    
    """
    ####################################################################################
    The following are the Update related tests
    """
    
    @defer.inlineCallbacks
    def test_save_and_load_update(self):
        input = Update(type ="update", name="TestUpdate",description = "A test description",)
        yield self._persistenceLayer.save_update(input)
        exp = input 
        obs = yield self._persistenceLayer.load_update(id = input._id)
        self.assertEquals(obs,exp)
    
    @defer.inlineCallbacks
    def test_save_and_load_updates(self):
        input =[]
        input.append(Update(name="TestUpdateOne",description = "A test description"))
        input.append(Update(name="TestUpdateTwo",description = "Another test description",status="active"))
       
        yield self._persistenceLayer.save_updates(input)
        exp = input 
        obs =  yield self._persistenceLayer.load_updates()
        self.assertEquals(obs,exp)
     
    @defer.inlineCallbacks
    def test_update_update(self):
        input = Update(name="TestUpdate",description = "A test description")
        yield self._persistenceLayer.save_update(input)
        input.name = "TestUpdateModified"
        yield self._persistenceLayer.save_update(input)
    
        exp = input
        obs = yield self._persistenceLayer.load_update(id = input._id)
        self.assertEquals(obs,exp)
    