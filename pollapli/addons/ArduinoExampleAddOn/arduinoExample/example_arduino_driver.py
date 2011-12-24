from twisted.plugin import IPlugin
from pollapli import ipollapli 
from zope.interface import classProvides
from twisted.internet import reactor, defer
from pollapli.core.hardware.drivers.protocols import BaseTextSerialProtocol
from pollapli.core.hardware.drivers.serial_hardware_interface import SerialHardwareInterface
from pollapli.core.hardware.drivers.driver import Driver


class ArduinoExampleProtocol(BaseTextSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case, the reprap 5D protocol (similar to teacup, but with checksum)
    """
    def __init__(self, driver=None, is_buffering=True, seperator='\n', *args, **kwargs):
        BaseTextSerialProtocol.__init__(self, driver, is_buffering, seperator)

    def _set_hardware_id(self, hardware_id=99):
        self.send_data("%i%s" % (hardware_id, str(self.driver.deviceId)))

    def _query_hardware_info(self):
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


class ArduinoExampleDriver(Driver):
    """Class defining the components of the driver for a basic arduino,using attached firmware """
    classProvides(IPlugin, ipollapli.IDriver)

    def __init__(self, options=None, *args, **kwargs):
        """
        very important : the first two args should ALWAYS be the CLASSES of the hardware handler and logic handler,
        and not instances of those classes
        """
        Driver.__init__(self, SerialHardwareInterface, ArduinoExampleProtocol, options, *args, **kwargs)

    def hello_world(self):
        self.send_command(0)
