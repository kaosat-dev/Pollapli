"""for now, no mock serial class, so this needs to be tested with an
actual, pre-configured Arduino"""
from twisted.trial import unittest
from pollapli.addons.ArduinoExampleAddOn.arduinoExample.example_arduino_driver import ExampleArduinoDriver
from twisted.internet import defer, reactor
from pollapli.core.hardware.drivers.serial_hardware_interface import SerialHardwareInterface
from twisted.internet.error import TimeoutError
from pollapli.core.hardware.commands import Command, GetFirmwareInfo
from twisted.python import log
import sys

log.startLogging(sys.stdout)


class TestExampleArduinoDriverCommands(unittest.TestCase):
    @defer.inlineCallbacks
    def setUp(self):
        self.ports = yield SerialHardwareInterface.list_ports()

    def tearDown(self):
        pass

    @defer.inlineCallbacks
    def test_call_send_info(self):
        driver = ExampleArduinoDriver(hardware_id="72442ba3-058c-4cee-a060-5d7c644f1dbe", do_hanshake=True, do_authentification=True, connection_timeout=0)
        yield driver.connect(port=self.ports[0], connection_mode=1)

        exp_response = "Name: Pollapli Arduino example firmware,Version: 0.1"
        obs_response = yield driver.get_firmware_info()
        self.assertEquals(obs_response, exp_response)
        driver.disconnect()

    @defer.inlineCallbacks
    def test_call_hello_world(self):
        driver = ExampleArduinoDriver(hardware_id="72442ba3-058c-4cee-a060-5d7c644f1dbe", do_hanshake=True, do_authentification=True, connection_timeout=0)
        yield driver.connect(port=self.ports[0], connection_mode=1)

        exp_response = "Hello python, Arduino here"
        obs_response = yield driver.hello_world()
        self.assertEquals(obs_response, exp_response)
        driver.disconnect()

    @defer.inlineCallbacks
    def test_call_get_hardware_id(self):
        driver = ExampleArduinoDriver(hardware_id="72442ba3-058c-4cee-a060-5d7c644f1dbe", do_hanshake=True, do_authentification=True, connection_timeout=0)
        yield driver.connect(port=self.ports[0], connection_mode=1)

        exp_response = "72442ba3-058c-4cee-a060-5d7c644f1dbe"
        obs_response = yield driver.get_hardware_id()
        self.assertEquals(obs_response, exp_response)
        driver.disconnect()
