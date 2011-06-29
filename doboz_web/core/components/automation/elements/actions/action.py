from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase

class Action(DBObject):
    BELONGSTO   = ['task']  
    def __init__(self,name="defaultAction",description="",*args,**kwargs):
        DBObject.__init__(self,**kwargs)