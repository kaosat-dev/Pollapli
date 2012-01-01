"""for now, no mock serial class, so this needs to be tested with an
actual, pre-configured Arduino"""
from twisted.trial import unittest
from pollapli.addons.ArduinoExampleAddOn.arduinoExample.example_arduino_driver import ExampleArduinoDriver
from twisted.internet import defer, reactor
from pollapli.core.hardware.drivers.serial_hardware_interface import SerialHardwareInterface
from twisted.internet.error import TimeoutError
from pollapli.core.hardware.commands import Command, GetFirmwareInfo, HelloWorld,\
    GetHardwareId
from twisted.python import log
import sys
from pollapli.core.logic.devices.device import Device

log.startLogging(sys.stdout)


class TestExampleArduinoDriverDevice(unittest.TestCase):
    @defer.inlineCallbacks
    def setUp(self):
        self.ports = yield SerialHardwareInterface.list_ports()

    def tearDown(self):
        pass

    @defer.inlineCallbacks
    def test_send_info_command(self):
        test_device = Device(name="TestDevice")
        driver = ExampleArduinoDriver(hardware_id="72442ba3-058c-4cee-a060-5d7c644f1dbe", do_hanshake=True, do_authentification=True, connection_timeout=0)
        test_device.driver = driver
        yield test_device.connect(port=self.ports[0], connection_mode=1)

        command = GetFirmwareInfo(device=test_device)
        exp_response = "Name: Pollapli Arduino example firmware,Version: 0.1"
        obs_response = yield command.run()
        self.assertEquals(obs_response, exp_response)
        test_device.disconnect()

    @defer.inlineCallbacks
    def test_send_hello_world_command(self):
        test_device = Device(name="TestDevice")
        driver = ExampleArduinoDriver(hardware_id="72442ba3-058c-4cee-a060-5d7c644f1dbe", do_hanshake=True, do_authentification=True, connection_timeout=0)
        test_device.driver = driver
        yield test_device.connect(port=self.ports[0], connection_mode=1)

        command = HelloWorld(device=test_device)
        exp_response = "Hello python, Arduino here"
        obs_response = yield command.run()
        self.assertEquals(obs_response, exp_response)
        driver.disconnect()

    @defer.inlineCallbacks
    def test_send_get_hardware_id_command(self):
        test_device = Device(name="TestDevice")
        driver = ExampleArduinoDriver(hardware_id="72442ba3-058c-4cee-a060-5d7c644f1dbe", do_hanshake=True, do_authentification=True, connection_timeout=0)
        test_device.driver = driver
        yield test_device.connect(port=self.ports[0], connection_mode=1)

        command = GetHardwareId(device=test_device)
        exp_response = "72442ba3-058c-4cee-a060-5d7c644f1dbe"
        obs_response = yield command.run()
        self.assertEquals(obs_response, exp_response)
        driver.disconnect()
