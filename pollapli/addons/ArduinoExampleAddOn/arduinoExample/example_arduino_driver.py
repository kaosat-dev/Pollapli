"""All classed for the arduino example driver (used for general reference)"""
from twisted.plugin import IPlugin
from pollapli import ipollapli
from zope.interface import classProvides
from twisted.internet import reactor, defer
from pollapli.core.hardware.drivers.protocols import BaseTextSerialProtocol
from pollapli.core.hardware.drivers.serial_hardware_interface import SerialHardwareInterface
from pollapli.core.hardware.drivers.driver import Driver


class ExampleArduinoProtocol(BaseTextSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case,just a
    simplified test protocol
    """
    def __init__(self, driver=None, is_buffering=True, seperator='\n', ref_handshake="start", *args, **kwargs):
        BaseTextSerialProtocol.__init__(self, driver, is_buffering, seperator, ref_handshake)

    def _set_hardware_id(self, hardware_id=99):
        self.send_data("%i%s" % (hardware_id, str(self.driver.deviceId)))

    def _query_hardware_id(self):
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


class ExampleArduinoDriver(Driver):
    """Class defining the components of the driver for a basic
     arduino,using attached firmware """
    classProvides(IPlugin, ipollapli.IDriver)

    def __init__(self, auto_connect=False, max_connection_errors=2,
        connection_timeout=4, speed=115200, *args, **kwargs):
        Driver.__init__(self, auto_connect, max_connection_errors, connection_timeout)
        self._hardware_interface = SerialHardwareInterface(self, ExampleArduinoProtocol, speed)

    def hello_world(self):
        """just a test"""
        self.send_command(0)
