from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from doboz_web.core.components.nodes.node import Node
import logging

class DummyCapability(DBObject):
    BELONGSTO   = ['node','environment']
    def __init__(self,info="reprapInfo",*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        log.msg("Dummy Capability Init Done", system="dummy node", logLevel=logging.CRITICAL)
            
    
Registry.register(Node, DummyCapability)