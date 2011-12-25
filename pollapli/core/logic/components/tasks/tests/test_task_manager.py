from pollapli.core.logic.components.tasks.task import Task
import os, logging, sys, shutil, 
from twisted.trial import unittest
from twisted.internet import reactor, defer
from twisted.python import log,failure
from pollapli.core.logic.tools.path_manager import PathManager
from pollapli.core.logic.components.tasks.task_manager import TaskManager
from pollapli.core.persistence.persistence_layer import PersistenceLayer

class TaskManagerFTest(unittest.TestCase):   
    
    @defer.inlineCallbacks
    def setUp(self):
        
        
        
        self._path_manager = PathManager()
        self._path_manager._addon_path = os.path.abspath("addons")
        self._path_manager.tmpPath = os.path.abspath("tmp")

        if not os.path.exists(self._path_manager.tmpPath):
            os.makedirs(self._path_manager.tmpPath)
        if not os.path.exists(self._path_manager._addon_path):
            os.makedirs(self._path_manager._addon_path)
            
        self._persistenceLayer = PersistenceLayer(pathManager=self._path_manager)
        self._taskManager = TaskManager(pathManager=self._path_manager)
       
        yield self._taskManager.setup()
       
    def tearDown(self):
        if os.path.exists(self._path_manager.tmpPath):
            shutil.rmtree(self._path_manager.tmpPath)
        if os.path.exists(self._path_manager._addon_path):
            shutil.rmtree(self._path_manager._addon_path)
                
    def test_add_task(self):
        task = self._taskManager.add_task("Test task", "a description", None, None)
        
    def test_add_task_condition(self):
        task = self._taskManager.add_task("Test task", "a description")
        self._taskManager.add_conditionToTask(id, condition)
        
        #self._taskManager.a