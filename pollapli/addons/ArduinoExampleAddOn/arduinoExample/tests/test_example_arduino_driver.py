"""for now, no mock serial class, so this needs to be tested with an
actual, pre-configured Arduino"""
from twisted.trial import unittest
from pollapli.addons.ArduinoExampleAddOn.arduinoExample.example_arduino_driver import ExampleArduinoDriver
from twisted.internet import defer, reactor
from pollapli.core.hardware.drivers.serial_hardware_interface import SerialHardwareInterface
import logging
from twisted.internet.error import TimeoutError
logger = logging.getLogger("Pollapli")


class TestExampleArduinoDriver(unittest.TestCase):
    @defer.inlineCallbacks
    def setUp(self):
        self.ports = yield SerialHardwareInterface.list_ports()

    def tearDown(self):
        pass

    @defer.inlineCallbacks
    def test_connect_setup_nohanshake_noauth(self):
        driver = ExampleArduinoDriver(do_hanshake=False, do_authentification=False, connection_timeout=0)
        yield driver.connect(port=self.ports[0], connection_mode=0)

        self.assertTrue(driver.is_connected)
        driver.disconnect()
        self.assertFalse(driver.is_connected)
        self.assertTrue(driver.is_configured)

    @defer.inlineCallbacks
    def test_connect_setup_hanshake_noauth(self):
        driver = ExampleArduinoDriver(do_hanshake=True, do_authentification=False, connection_timeout=0)
        yield driver.connect(port=self.ports[0], connection_mode=0)

        self.assertTrue(driver.is_connected)
        driver.disconnect()
        self.assertFalse(driver.is_connected)
        self.assertTrue(driver.is_configured)

    @defer.inlineCallbacks
    def test_connect_setup_hanshake_auth(self):
        driver = ExampleArduinoDriver(do_hanshake=True, do_authentification=True, connection_timeout=0)
        yield driver.connect(port=self.ports[0], connection_mode=0)
        self.assertTrue(driver.is_connected)
        driver.disconnect()
        self.assertFalse(driver.is_connected)
        self.assertTrue(driver.is_configured)
        self.assertEquals(driver.hardware_id, "72442ba3-058c-4cee-a060-5d7c644f1dbe")

    @defer.inlineCallbacks
    def test_connect_normal_nohanshake_noauth(self):
        driver = ExampleArduinoDriver(do_hanshake=False, do_authentification=False, connection_timeout=0)
        yield driver.connect(port=self.ports[0], connection_mode=1)

        self.assertTrue(driver.is_connected)
        driver.disconnect()
        self.assertFalse(driver.is_connected)

    @defer.inlineCallbacks
    def test_connect_normal_hanshake_noauth(self):
        driver = ExampleArduinoDriver(do_hanshake=True, do_authentification=False, connection_timeout=0)
        yield driver.connect(port=self.ports[0], connection_mode=1)

        self.assertTrue(driver.is_connected)
        driver.disconnect()
        self.assertFalse(driver.is_connected)

    @defer.inlineCallbacks
    def test_connect_normal_hanshake_auth(self):
        driver = ExampleArduinoDriver(hardware_id="72442ba3-058c-4cee-a060-5d7c644f1dbe",do_hanshake=True, do_authentification=True, connection_timeout=0)
        yield driver.connect(port=self.ports[0], connection_mode=1)

        self.assertTrue(driver.is_connected)
        driver.disconnect()
        self.assertFalse(driver.is_connected)

    def test_connect_normal_hanshake_auth_timeout_failure(self):
        driver = ExampleArduinoDriver(do_hanshake=True, do_authentification=True, connection_timeout=0.2)
        deferred = driver.connect(port=self.ports[0], connection_mode=1)
        return self.assertFailure(deferred,TimeoutError)

    @defer.inlineCallbacks
    def test_connect_normal_hanshake_auth_timeout(self):
        driver = ExampleArduinoDriver(hardware_id="72442ba3-058c-4cee-a060-5d7c644f1dbe",do_hanshake=True, do_authentification=True, connection_timeout=2)
        yield driver.connect(port=self.ports[0], connection_mode=1)

        self.assertTrue(driver.is_connected)
        driver.disconnect()
        self.assertFalse(driver.is_connected)
