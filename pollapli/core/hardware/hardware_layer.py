"""main module and entry point for the hardware layer, handling all
interactions with actual hardware"""
from twisted.internet import defer
from pollapli import ipollapli
from pollapli.core.hardware.drivers.driver_manager import DriverManager
from pollapli.exceptions import UnknownDriver


class HardwareLayer(object):
    """main hardware layer class"""
    def __init__(self, package_manager=None, hardware_poll_frequency=3):
        self._package_manager = package_manager
        self._driver_manager = DriverManager(hardware_poll_frequency)

    def setup(self):
        pass

    def teardown(self):
        pass

    @defer.inlineCallbacks
    def add_driver(self, driver_type=None, driver_params=None):
        if driver_type is None:
            raise UnknownDriver()
        plugins = (yield self._package_manager.get_plugins(ipollapli.IDriver))
        driver = None

        for driver_class in plugins:
            if driver_type == driver_class.__name__.lower():
                driver = self._driver_manager.add_driver(driver_class, **driver_params)
                break
        if not driver:
            raise UnknownDriver()

    @defer.inlineCallbacks
    def get_driver_types(self): 
        driver_types_tmp = yield PackageManager.get_plugins(ipollapli.IDriver)
        driver_types = [driver_type_inst() for driver_type_inst in driver_types_tmp]
        defer.returnValue(driver_types)
