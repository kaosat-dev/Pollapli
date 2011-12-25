from twisted.trial import unittest
from twisted.internet import defer
from pollapli.core.hardware.drivers.driver_manager import DriverManager
from pollapli.core.hardware.drivers.driver import Driver
from pollapli.core.hardware.drivers.tests.mock_driver import MockDriver,\
    MockHardwareInterface


class Test(unittest.TestCase):

    def setUp(self):
        self._driverManager = DriverManager()

    def tearDown(self):
        pass

    def test_add_driver(self):
        driver_class = MockDriver
        exp_driver = MockDriver()
        obs_driver = self._driverManager.add_driver(driver_class)

        self.assertEquals(obs_driver, exp_driver)

    def test_get_driver(self):
        driver_class = MockDriver
        exp_driver = self._driverManager.add_driver(driver_class)
        obs_driver = self._driverManager.get_driver(driver_id=exp_driver.cid)

        self.assertEquals(obs_driver, exp_driver)

    @defer.inlineCallbacks
    def test_get_drivers(self):
        driver_class = MockDriver
        exp_driver1 = self._driverManager.add_driver(driver_class)
        exp_driver2 = self._driverManager.add_driver(driver_class)

        l_exp_drivers = sorted([exp_driver1, exp_driver2])
        l_obs_drivers = sorted((yield self._driverManager.get_drivers()))

        self.assertEquals(l_exp_drivers, l_obs_drivers)

    @defer.inlineCallbacks
    def test_get_drivers_filtered(self):
        driver_class = MockDriver
        exp_driver1 = self._driverManager.add_driver(driver_class)
        exp_driver2 = self._driverManager.add_driver(driver_class)
        self._driverManager.add_driver(driver_class)

        l_exp_drivers = sorted([exp_driver1, exp_driver2])
        l_obs_drivers = sorted((yield self._driverManager.get_drivers({"cid": [exp_driver1.cid, exp_driver2.cid]})))

        self.assertEquals(l_exp_drivers, l_obs_drivers)

    @defer.inlineCallbacks
    def test_delete_driver(self):
        driver_class = MockDriver
        exp_driver1 = self._driverManager.add_driver(driver_class)
        exp_driver2 = self._driverManager.add_driver(driver_class)

        yield self._driverManager.delete_driver(exp_driver2.cid)

        l_exp_drivers = sorted([exp_driver1])
        l_obs_drivers = sorted((yield self._driverManager.get_drivers()))

        self.assertEquals(l_exp_drivers, l_obs_drivers)

    @defer.inlineCallbacks
    def test_clear_drivers(self):
        driver_class = MockDriver
        self._driverManager.add_driver(driver_class)
        self._driverManager.add_driver(driver_class)
        self._driverManager.add_driver(driver_class)

        yield self._driverManager.clear_drivers()
        l_exp_drivers = []
        l_obs_drivers = yield self._driverManager.get_drivers()

        self.assertEquals(l_exp_drivers, l_obs_drivers)

#    @defer.inlineCallbacks
#    def test_get_unbound_ports(self):
#        driver_class = MockDriver
#        driver = self._driverManager.add_driver(driver_class)
#        MockHardwareInterface.available_ports = ["port1"]
#        yield self._driverManager.update_device_list()
#        obs_ubound_ports = self._driverManager.get_unbound_ports(driver.hardware_interface_class)
#        exp_ubound_ports = ["port1"]
#        self.assertEquals(obs_ubound_ports, exp_ubound_ports)


    def test_connect_driver(self):
        pass

    def test_disconnect_driver(self):
        pass

    def test_upload_firmware(self):
        pass
