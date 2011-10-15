import logging,ast,time
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from zope.interface import Interface, Attribute,implements
from twisted.plugin import IPlugin,getPlugins
from twisted.internet.protocol import Protocol

from doboz_web.exceptions import UnknownDriver,NoDriverSet,DeviceIdMismatch,DeviceNotConnected
from doboz_web import idoboz_web
from doboz_web.core.tools.signal_system import SignalHander
from doboz_web.core.components.updates.update_manager import UpdateManager

class Firmware(object):
    """firmware class for encapsulating info about firmware files + added helpers"""
    #need to find the right place to store all paths to arduino files etc
    pass