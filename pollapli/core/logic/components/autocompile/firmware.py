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

from pollapli.exceptions import UnknownDriver,NoDriverSet,DeviceIdMismatch,DeviceNotConnected
from pollapli import ipollapli
from pollapli.core.logic.tools.signal_system import SignalHander
from pollapli.core.logic.components.updates.update_manager import UpdateManager

class Firmware(object):
    """firmware class for encapsulating info about firmware files + added helpers"""
    #need to find the right place to store all paths to arduino files etc
    pass