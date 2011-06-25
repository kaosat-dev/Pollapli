from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

from doboz_web.core.components.connectors.hardware.hardware_connector import HardwareConnector,HardwareConnectorEvents
from twisted.internet import protocol

class BaseProtocolTest(protocol.Protocol):
    def dataReceived(self, data):
        for c in data:
            byte = ord(c)
            #self.state = getattr(self, 'state_'+self.state)(byte)

class SerialTwisted(HardwareConnector):
    pass