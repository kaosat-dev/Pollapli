from twisted.trial import unittest
from pollapli.core.hardware.drivers.driver_manager import DriverManager


class Test(unittest.TestCase):

    def setUp(self):
        self._driverManager = DriverManager()

    def tearDown(self):
        pass

    def test_add_driver(self):
        pass#self._driverManager.add_driver(driver)

    def test_update_device_ist(self):
        pass

    def test_connect_driver(self):
        pass

    def test_disconnect_driver(self):
        pass
