from zope.interface import implements
from twisted.plugin import IPlugin
from pollapli import ipollapli 
from zope.interface import classProvides
from twisted.python import log,failure
from twisted.internet import reactor, defer
import uuid,logging
from pollapli.exceptions import DeviceHandshakeMismatch,DeviceIdMismatch
from pollapli.core.hardware.drivers.protocols import BaseTextSerialProtocol
from pollapli.core.hardware.drivers.driver import Driver

class ReprapBaseProtocol(BaseTextSerialProtocol):
    """
    Class defining the protocol used by this driver: in this case, the reprap teacup protocol 
    which is the most straighforward of reprap protocols (no checksum etc)
    """
    def __init__(self,driver=None,is_buffering=True,seperator='\n',*args,**kwargs):
        BaseTextSerialProtocol.__init__(self,driver,is_buffering,seperator)

    def _format_data_out(self,data,*args,**kwargs):
        """
        Formats an outgoing block of data according to some specs/protocol 
        data: the outgoing data to the device
        """
        data=data.split(';')[0]
        data=data.strip()
        data=data.replace(' ','')
        data=data.replace("\t",'')
        return data+ "\n"


class BaseReprapDriver(Driver):
    """Class defining the generic reprap driver components"""
    classProvides(IPlugin, ipollapli.IDriver)
    target_hardware = "Reprap"

    def __init__(self, auto_connect=False, max_connection_errors=3,
        connection_timeout=0, do_hanshake=True, do_authentifaction=True,
        speed=115200, *args, **kwargs):
        """
        very important : the first two args should ALWAYS be the CLASSES of the hardware handler and logic handler,
        and not instances of those classes
        """
        Driver.__init__(self, auto_connect, max_connection_errors, connection_timeout, do_hanshake, do_authentifaction)

    """ generic"""
    def get_firmware_version(self):
        raise NotImplementedError()

    def queue_position(self, position, extended=False, absolute=True, rapid=False):
        raise NotImplementedError()

    def get_position(self, extended=False):
        raise NotImplementedError()

    def set_position(self, position, extended=False):
        raise NotImplementedError()

    def save_homePosition(self):
        raise NotImplementedError()

    def load_homePosition(self):
        raise NotImplementedError()

    def go_homePosition(self):
        raise NotImplementedError()

    def set_unit(self, unit="mm"):
        raise NotImplementedError()
