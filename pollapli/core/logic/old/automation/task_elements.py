from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase

class TaskComponent(Object):
    def __init__(self):
        self.id=-1
        
class Action(DBObject):
    BELONGSTO   = ['task']  
    def __init__(self,name="defaultAction",description="",*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.repeater=False
        self.deferred=defer.Deferred()
        return d
    
"""
####################################################################################
The following are Conditions related classes
"""
    
class ConditionEvents(Events):
    """
    Class defining events associated to HardwareConnector Class
    """
    __events__=('validated','invalidated')

       
class Condition(DBObject):
    BELONGSTO   = ['task']  
    """A condition is similar to a boolean expression: it must return
    true or false in its call method """
    def __init__(self,name="defaultCondition",description="",critical=False,*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.events=ConditionEvents()
        self.critical=critical#is this a critical condition
        self.valid=False
        
    def validate(self):
        self.valid=True
        self.events.validated(self)
    
    def invalidate(self):
        self.valid=False
        self.events.invalidated(self)