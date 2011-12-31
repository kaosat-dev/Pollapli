import unittest
from twisted.trial.runner import TestSuite, suiteVisit


TestDriverManagerSuite = unittest.TestLoader().loadTestsFromTestCase(TestDriverManager) 
DriverManagerExampleArduinoDriverSuite = unittest.TestLoader().loadTestsFromTestCase(TestDriverManagerExampleArduinoDriver)
TestHardwareLayerSuite = unittest.TestLoader().loadTestsFromTestCase(TestHardwareLayer)