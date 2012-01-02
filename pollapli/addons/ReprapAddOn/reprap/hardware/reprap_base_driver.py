from zope.interface import implements
from twisted.plugin import IPlugin
from pollapli import ipollapli 
from zope.interface import classProvides
from twisted.python import log,failure
from twisted.internet import reactor, defer
import uuid,logging
from pollapli.core.hardware.drivers.driver import Driver


class ReprapBaseDriver(Driver):
    """Class defining the generic reprap driver components"""
    classProvides(IPlugin, ipollapli.IDriver)
    target_hardware = "Reprap"

    def __init__(self, hardware_id=None, auto_connect=False,
        max_connection_errors=3, connection_timeout=4, do_hanshake=True,
        do_authentification=True, speed=115200):
        Driver.__init__(self, hardware_id, auto_connect, max_connection_errors, connection_timeout, do_hanshake, do_authentification)

    def enqueue_position(self, position, rapid=False):
        raise NotImplementedError()

    def get_position(self):
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
