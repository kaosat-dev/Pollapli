from twisted.trial import unittest
from pollapli.core.logic.components.environment import EnvironmentManager
 
class SchedulerTest(unittest.TestCase):
    def setUp(self):
        self.environmentManager=EnvironmentManager()
        
    def tearDown(self):
        self.environmentManager=None
        
    def test_simpleScheduler(self):
        pass
    
   