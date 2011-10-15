from twisted.trial import unittest
from doboz_web.core.logic.components.environment import EnvironmentManager
 
class ProtocolTest(unittest.TestCase):
    def setUp(self):
        self.environmentManager=EnvironmentManager()
        
    def tearDown(self):
        self.environmentManager=None
        
    def test_connectionMade(self):
        pass
    def test_connectionLost(self):
        pass
    
    def test_dataReceived(self):
        pass
    
   