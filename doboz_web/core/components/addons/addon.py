from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

class AddOn(DBObject):
     def __init__(self,name="node",description="add on",*args,**kwargs):
        DBObject.__init__(self,**kwargs)