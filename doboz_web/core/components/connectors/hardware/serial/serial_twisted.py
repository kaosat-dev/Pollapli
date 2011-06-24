from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

from doboz_web.core.components.connectors.hardware.hardware_connector import HardwareConnector,HardwareConnectorEvents


class SerialTwisted(HardwareConnector):
    pass