import unittest
from twisted.trial.runner import TestSuite, suiteVisit
from pollapli.core.hardware.drivers.tests.test_driver_manager_example_arduino_driver import TestDriverManagerExampleArduinoDriver
from pollapli.core.hardware.drivers.tests.test_driver_manager import TestDriverManager
from pollapli.core.hardware.tests.test_hardware_layer import TestHardwareLayer

TestDriverManagerSuite = unittest.TestLoader().loadTestsFromTestCase(TestDriverManager) 
DriverManagerExampleArduinoDriverSuite = unittest.TestLoader().loadTestsFromTestCase(TestDriverManagerExampleArduinoDriver)
TestHardwareLayerSuite = unittest.TestLoader().loadTestsFromTestCase(TestHardwareLayer)