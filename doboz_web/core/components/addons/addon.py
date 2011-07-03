from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

class AddOn(DBObject):
    def __init__(self,name="node",description="add on",path="",*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.enabled=False
        self.name=name
        self.description=description
        self.path=path
        
    def _toDict(self):
        return {"AddOn":{"name":self.name,"description":"","active":self.enabled,"path":self.path}}