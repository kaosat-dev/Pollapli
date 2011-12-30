from twisted.trial import unittest
from twisted.internet import defer
from pollapli.core.hardware.hardware_layer import HardwareLayer
from pollapli.core.hardware.drivers.tests.mock_driver import MockDriver
from pollapli.core.logic.components.packages.package_manager import PackageManager


class TestHardwareLayer(unittest.TestCase):

    def setUp(self):
        self._package_manager = PackageManager()
        self._hardware_layer = HardwareLayer(self._package_manager)

    def tearDown(self):
        pass

    @defer.inlineCallbacks
    def test_add_driver(self):
        exp_driver = MockDriver()
        obs_driver = yield self._hardware_layer.add_driver("MockDriver")

        self.assertEquals(obs_driver, exp_driver)

