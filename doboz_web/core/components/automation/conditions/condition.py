from doboz_web.core.tools.event_sys import *


class ConditionEvents(Events):
    """
    Class defining events associated to HardwareConnector Class
    """
    __events__=('validated','invalidated')


class Condition(object):
    """A condition is similar to a boolean expression: it must return
    true or false in its call method """
    def __init__(self,critical=False):
        self.events=ConditionEvents()
        self.critical=critical#is this a critical condition
        self.valid=False
        
    def validate(self):
        self.valid=True
        self.events.validated(self)
    
    def invalidate(self):
        self.valid=False
        self.events.invalidated(self)