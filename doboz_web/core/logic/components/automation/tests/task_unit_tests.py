from twisted.trial import unittest
from doboz_web.core.logic.components.environment import EnvironmentManager
 
class TaskTest(unittest.TestCase):
    def setUp(self):
        self.environmentManager=EnvironmentManager()
        
    def tearDown(self):
        self.environmentManager=None
        
    def test_driverCreation(self):
        pass
    
    def test_driverUpdate(self):
        pass
    
    def test_driverDeletion(self):
        pass
    
    def test_deviceDetection(self):
        pass
    
    def test_devicePluggedIn(self):
        pass
    
    def test_devicePluggedOut(self):
        pass
    