import logging, uuid, pkgutil,zipfile ,os,sys,json,shutil,time,traceback,datetime
from zipfile import ZipFile
from twisted.internet import reactor, defer,task
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

class Schedule(object):
    def __init__(self,seconds=0,minutes=0,hours=0,months=0,doms=0,dows=0,cronLine=None,*args,**kwargs):
        if cronLine is not None:
            self.parse_cronLine(cronLine)
        else:
            self.seconds=seconds
            self.minutes=minutes
            self.hours=hours
            self.months=months
            self.dows=dows# days of the week
            self.doms=doms# days of the month
        
    def parse_cronLine(self,cronLine):
        pass
    
    def __eq__(self,other):
        if not isinstance(other,Schedule):
            return False
        return self.seconds == other.seconds and self.minutes == other.minutes and self.hours == other.hours \
    and self.months == other.months and self.dows == other.dows and self.doms == other.doms
    
    def get_next_instance(self):
        pass
    
    def get_delay_for_next(self):
        pass
    
class ScheduledCall(object):
    def __init__(self,callback,startTime,repeatTime=None):  
        self.start_time=startTime
        self.repeatTime=repeatTime
        self._lastTime=None
        self.callback=callback
        self.running=False
             
    def start(self):
        if self.running:
            raise Exception("Scheduled call is already running")
        self.deferred=defer.Deferred()
        return self.deferred
    
    def stop(self):
        pass
    
    def _next_time(self):
        interval=0
        
    def _reschedule(self):
        delay=self._next_time()
        self._lastTime=reactor.seconds()
        self.call=reactor.callLater(delay,self.callback)

class Scheduler(object):
    cls.updateCheck= task.LoopingCall(cls.refresh_updateList)
    cls.updateCheck.start(interval=240,now=False)