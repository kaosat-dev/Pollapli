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
    def __init__(self, driver=None, handshake="start", seperator='\n', *args, **kwargs):
        BaseTextSerialProtocol.__init__(self, driver, handshake, seperator)

    def _format_data_in(self, data):
        """
        Formats an incomming data block according to some specs/protocol
        :param data: the incomming data from the device
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
     Arduino, using attached firmware """
    classProvides(IPlugin, ipollapli.IDriver)
    target_hardware = "Generic_arduino"

    def __init__(self, auto_connect=False, max_connection_errors=3,
        connection_timeout=0, do_hanshake=True, do_authentifaction=True,
        speed=115200, *args, **kwargs):
        Driver.__init__(self, auto_connect, max_connection_errors, connection_timeout, do_hanshake, do_authentifaction)
        self._hardware_interface = SerialHardwareInterface(self, ExampleArduinoProtocol, speed)

    def set_hardware_id(self, hardware_id=None):
        self.send_command("99%i" % (hardware_id))

    def get_hardware_id(self):
        """method for retrieval of hardware_id """
        self.send_command("2")

    def hello_world(self):
        """just a test"""
        self.send_command(0)
