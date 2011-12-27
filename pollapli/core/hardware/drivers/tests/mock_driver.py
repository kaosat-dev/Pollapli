"""A mock driver, for tests"""
from twisted.plugin import IPlugin
from pollapli import ipollapli
from zope.interface import classProvides
from twisted.internet import reactor, defer
from pollapli.core.hardware.drivers.protocols import BaseProtocol
from pollapli.core.hardware.drivers.serial_hardware_interface import SerialHardwareInterface
from pollapli.core.hardware.drivers.driver import Driver
from pollapli.core.hardware.drivers.hardware_interfaces import BaseHardwareInterface


class MockHardwareInterface(BaseHardwareInterface):
    """class handling the connection to mock devices"""
    def __init__(self, driver=None, protocol=None, speed=9200, *args, **kwargs):
        BaseHardwareInterface.__init__(self, driver, protocol, *args, **kwargs)

    @classmethod
    def list_ports(cls):
        """
        Return a list of ports
        """
        deferred = defer.Deferred()

        def _list_ports(*args, **kwargs):
            foundPorts = ["port1"]
            return foundPorts

        reactor.callLater(0.1, deferred.callback, None)
        deferred.addCallback(_list_ports)
        return deferred


class MockProtocol(BaseProtocol):
    """
    Class defining the protocol used by this driver: in this case,just a
    simplified test protocol
    """
    def __init__(self, driver=None, is_buffering=True, seperator='\n', *args, **kwargs):
        BaseProtocol.__init__(self, driver, None)

    def _set_hardware_id(self, hardware_id=99):
        self.send_data("%i%s" % (hardware_id, str(self.driver.deviceId)))

    def _get_hardware_id(self):
        """method for retrieval of device info (for hardware_id and more) """
        self.send_data("2")

    def _format_data_in(self, data, *args, **kwargs):
        """
        Formats an incomming data block according to some specs/protocol
        data: the incomming data from the device
        """
        if " " in data:
            data = "".join(data.split(" ")[1:])
        data = data.replace("ok", '')
        data = data.replace(" ", '')
        data = data.replace('\n', '')
        data = data.replace('\r', '')
        return data


class MockDriver(Driver):
    """Class defining the components of the driver for a basic
     arduino,using attached firmware """
    classProvides(IPlugin, ipollapli.IDriver)

    def __init__(self, auto_connect=False, max_connection_errors=2,
        connection_timeout=4, speed=115200, *args, **kwargs):
        Driver.__init__(self, auto_connect, max_connection_errors, connection_timeout)
        self._hardware_interface = MockHardwareInterface(self, MockProtocol, speed)

    def hello_world(self):
        """just a test"""
        self.send_command(0)
