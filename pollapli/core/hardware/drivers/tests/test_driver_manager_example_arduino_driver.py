from twisted.trial import unittest
from twisted.internet import defer, reactor
from twisted.python import log
from pollapli.core.hardware.drivers.driver_manager import DriverManager
from pollapli.core.hardware.drivers.driver import Driver
from pollapli.addons.ArduinoExampleAddOn.arduinoExample.example_arduino_driver import ExampleArduinoDriver
import sys

#log.startLogging(sys.stdout)


class TestDriverManagerExampleArduinoDriver(unittest.TestCase):

    def setUp(self):
#        self.observer = log.PythonLoggingObserver()
#        self.observer.start()
        self._driverManager = DriverManager()

    def tearDown(self):
        pass
#        self.observer.stop()

    @defer.inlineCallbacks
    def test_binding(self):
        driver_class = ExampleArduinoDriver
        driver = self._driverManager.add_driver(driver_class, hardware_id="72442ba3-058c-4cee-a060-5d7c644f1dbe", connection_timeout=2)
        yield self._driverManager.update_device_list()
        self.assertTrue(driver.is_bound)
        self._driverManager.teardown()

    @defer.inlineCallbacks
    def test_binding_failure_no_id_doauth(self):
        driver_class = ExampleArduinoDriver
        driver = self._driverManager.add_driver(driver_class, connection_timeout=2)
        yield self._driverManager.update_device_list()
        self.assertFalse(driver.is_bound)
        self._driverManager.teardown()

    @defer.inlineCallbacks
    def test_binding_failure_id_noauth(self):
        driver_class = ExampleArduinoDriver
        driver = self._driverManager.add_driver(driver_class, hardware_id="72442ba3-058c-4cee-a060-5d7c644f1dbe", do_authentification=False, connection_timeout=2)
        yield self._driverManager.update_device_list()
        self.assertFalse(driver.is_bound)
        self._driverManager.teardown()

    @defer.inlineCallbacks
    def test_binding_failure_id_doauth_timeout(self):
        driver_class = ExampleArduinoDriver
        driver = self._driverManager.add_driver(driver_class, hardware_id="72442ba3-058c-4cee-a060-5d7c644f1dbe", connection_timeout=0.1)
        yield self._driverManager.update_device_list()
        self.assertFalse(driver.is_bound)
        self._driverManager.teardown()

    @defer.inlineCallbacks
    def test_connect_hardware_forced_noport(self):
        driver_class = ExampleArduinoDriver
        driver = self._driverManager.add_driver(driver_class, connection_timeout=2)
        yield self._driverManager.update_device_list()
        yield self._driverManager.connect_to_hardware(driver.cid, port=None, connection_mode=2)

        self.assertTrue(driver.is_connected)
        self._driverManager.teardown()

    @defer.inlineCallbacks
    def test_connect_hardware_setup_noport(self):
        driver_class = ExampleArduinoDriver
        driver = self._driverManager.add_driver(driver_class, connection_timeout=2)
        yield self._driverManager.update_device_list()
        yield self._driverManager.connect_to_hardware(driver.cid, port=None, connection_mode=0)

        self.assertTrue(driver.is_connected)
        self.assertEquals(driver.hardware_id, "72442ba3-058c-4cee-a060-5d7c644f1dbe")
        self._driverManager.teardown()
