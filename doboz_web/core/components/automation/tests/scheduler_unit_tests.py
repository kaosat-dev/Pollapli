from twisted.trial import unittest
from doboz_web.core.components.environment import EnvironmentManager
 
class SchedulerTest(unittest.TestCase):
    def setUp(self):
        self.environmentManager=EnvironmentManager()
        
    def tearDown(self):
        self.environmentManager=None
        
    def test_simpleScheduler(self):
        pass
    
   