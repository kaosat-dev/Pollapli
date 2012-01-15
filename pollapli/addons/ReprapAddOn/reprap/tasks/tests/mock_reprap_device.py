from pollapli.core.logic.devices.device import Device
from twisted.internet import defer, reactor


class MockReprapDevice(Device):
    """A mock reprap device class"""
    def __init__(self, name="mock reprap", description="a mock reprap", environment="Home", command_delay=0.2):
        Device.__init__(self, name, description, environment)
        self.command_delay = command_delay

    def set_variable_target(self, variable=None, value=None):
        deferred = defer.Deferred()

        def do_some_mock_stuff(result):
            return (variable, value)

        deferred.addCallback(do_some_mock_stuff)
        reactor.callLater(self.command_delay, deferred.callback, None)
        return deferred
