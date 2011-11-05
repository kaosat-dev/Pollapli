from twisted.trial import unittest
from pollapli.run import *
from pollapli.core.logic.components.environment import EnvironmentManager
 
class EnvironmentTest(unittest.TestCase):
    def setUp(self):
        configure_all() 
        self.environmentManager=EnvironmentManager()
        
    def tearDown(self):
        self.environmentManager=None
        
    def test_environmentCreation(self):
        self.environmentManager
    
    def test_environmentUpdate(self):
        pass
    
    def test_environmentDeletion(self):
        pass