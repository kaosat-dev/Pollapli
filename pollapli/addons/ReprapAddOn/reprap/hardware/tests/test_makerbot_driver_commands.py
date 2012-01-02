"""for now, no mock serial class, so this needs to be tested with an
actual, pre-configured Arduino"""
from twisted.trial import unittest
from twisted.internet import defer, reactor
from twisted.internet.error import TimeoutError

from twisted.python import log
import sys
from pollapli.addons.ReprapAddOn.reprap.hardware.reprap_makerbot_driver import ReprapMakerbotDriver
from pollapli.core.hardware.drivers.serial_hardware_interface import SerialHardwareInterface

log.startLogging(sys.stdout)


class TestMakerbotDriverCommands(unittest.TestCase):
    @defer.inlineCallbacks
    def setUp(self):
        self.ports = yield SerialHardwareInterface.list_ports()

    def tearDown(self):
        pass

#    @defer.inlineCallbacks
#    def test_call_send_info(self):
#        driver = ReprapMakerbotDriver(onnection_timeout=0)
#        yield driver.connect(port=self.ports[0], connection_mode=1)
#
#        exp_response = "Name: Pollapli Arduino example firmware,Version: 0.1"
#        obs_response = yield driver.get_firmware_info()
#        self.assertEquals(obs_response, exp_response)
#        driver.disconnect()

    @defer.inlineCallbacks
    def test_call_startup(self):
        driver = ReprapMakerbotDriver(connection_timeout=4)
        yield driver.connect(port=self.ports[0], connection_mode=1)

        exp_response = "Name: Pollapli Arduino example firmware,Version: 0.1"
        obs_response = yield driver.startup()
        self.assertEquals(obs_response, exp_response)
        driver.disconnect()
