from twisted.trial import unittest
from pollapli.run import *


class EnvironmentTest(unittest.TestCase):
    def setUp(self):
       configure_all() 
        
    def tearDown(self):
        pass
        
    def test_mainRun(self):
        pass
    