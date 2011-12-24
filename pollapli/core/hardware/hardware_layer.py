from twisted.internet import defer
from pollapli import ipollapli


class HardwareLayer(object):
    def __init__(self):
        pass

    def setup(self):
        pass

    def teardown(self):
        pass

    @defer.inlineCallbacks
    def get_driverTypes(self, *args, **kwargs): 
        driver_types_tmp = yield PackageManager.get_plugins(ipollapli.IDriver)
        driver_types = [driverTypeInst() for driverTypeInst in driver_types_tmp]
        defer.returnValue(driver_types)