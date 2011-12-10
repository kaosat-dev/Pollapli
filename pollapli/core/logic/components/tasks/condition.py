from pollapli.core.logic.tools.event_sys import *
from twisted.internet import reactor, defer



class Condition(object):
    def __init__(self, isValid=False, schedule = None):
        self.isValid = isValid
        self.schedule = schedule
        self._validationCallbacks = []
        self._invalidationCallbacks = []
        
    def addValidationCallback(self, callback, *args, **kwargs):
        self._validationCallbacks.append(callback)
        
    def removeValidationCallback(self,callback):
        self._validationCallbacks.remove(callback)
    
    def addInValidationCallback(self, callback, *args, **kwargs):
        self._invalidationCallbacks.append(callback)
        
    def removeInValidationCallback(self,callback):
        self._invalidationCallbacks.remove(callback)
    
    def validated(self):
        pass
    
    def invalidated(self):
        pass
    
#condition sets : based on conditions, using the same interface as conditions, but acting as an interface
#for a group of conditions
#subclass of conditions ?
#conditions: trigger on validation and invalidation, (different actions for those two cases, and while active)