"""main module and entry point for the hardware layer, handling all
interactions with actual hardware"""
from twisted.internet import defer
from pollapli import ipollapli
from pollapli.core.logic.components.packages.package_manager import PackageManager


class HardwareLayer(object):
    """main hardware layer class"""
    def __init__(self, package_manager):
        self._package_manager = package_manager

    def setup(self):
        pass

    def teardown(self):
        pass

    @defer.inlineCallbacks
    def get_driver_types(self): 
        driver_types_tmp = yield PackageManager.get_plugins(ipollapli.IDriver)
        driver_types = [driver_type_inst() for driver_type_inst in driver_types_tmp]
        defer.returnValue(driver_types)
